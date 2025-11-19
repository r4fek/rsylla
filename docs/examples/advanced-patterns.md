# Advanced Usage Patterns

This document demonstrates advanced patterns and real-world use cases for rsylla.

## 1. Multi-Tenant Application

```python
from rsylla import Session, SessionBuilder
import threading

class MultiTenantDatabase:
    """Database handler for multi-tenant application"""

    def __init__(self, nodes):
        self.session = (
            SessionBuilder()
            .known_nodes(nodes)
            .pool_size(30)
            .compression("lz4")
            .build()
        )

        self._tenant_stmts = {}
        self._lock = threading.Lock()

    def get_tenant_data(self, tenant_id, user_id):
        """Get data for specific tenant"""
        # Prepare statement per tenant for better caching
        stmt_key = f"get_user_{tenant_id}"

        with self._lock:
            if stmt_key not in self._tenant_stmts:
                self._tenant_stmts[stmt_key] = self.session.prepare(
                    f"SELECT * FROM tenant_{tenant_id}.users WHERE id = ?"
                ).set_idempotent(True)

        stmt = self._tenant_stmts[stmt_key]
        result = self.session.execute_prepared(stmt, {"id": user_id})
        return result.first_row()

    def create_tenant_schema(self, tenant_id):
        """Create keyspace and tables for new tenant"""
        # Create tenant keyspace
        self.session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS tenant_{tenant_id}
            WITH replication = {{
                'class': 'NetworkTopologyStrategy',
                'dc1': 3
            }}
        """)

        self.session.use_keyspace(f"tenant_{tenant_id}", False)

        # Create tables
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id int PRIMARY KEY,
                name text,
                email text,
                created_at timestamp
            )
        """)

        self.session.execute("""
            CREATE TABLE IF NOT EXISTS events (
                user_id int,
                event_time timestamp,
                event_type text,
                data map<text, text>,
                PRIMARY KEY (user_id, event_time)
            ) WITH CLUSTERING ORDER BY (event_time DESC)
        """)

        self.session.await_schema_agreement()

# Usage
db = MultiTenantDatabase(["localhost:9042"])

# Create tenant
db.create_tenant_schema(1001)

# Access tenant data
user = db.get_tenant_data(1001, 123)
```

## 2. Time Series Data

```python
from rsylla import Session, Batch
from datetime import datetime, timedelta
import time

class TimeSeriesStore:
    """Store and query time series data efficiently"""

    def __init__(self, session):
        self.session = session
        self._setup_schema()

    def _setup_schema(self):
        """Create optimized time series table"""
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                metric_name text,
                bucket date,
                timestamp timestamp,
                value double,
                tags map<text, text>,
                PRIMARY KEY ((metric_name, bucket), timestamp)
            ) WITH CLUSTERING ORDER BY (timestamp DESC)
            AND compaction = {
                'class': 'TimeWindowCompactionStrategy',
                'compaction_window_unit': 'DAYS',
                'compaction_window_size': 1
            }
        """)

        self.insert_stmt = self.session.prepare("""
            INSERT INTO metrics (metric_name, bucket, timestamp, value, tags)
            VALUES (?, ?, ?, ?, ?)
            USING TTL ?
        """)

    def insert_metric(self, metric_name, value, tags=None, ttl_seconds=86400):
        """Insert a metric data point"""
        now = datetime.utcnow()
        bucket = now.date()
        timestamp = int(now.timestamp() * 1000)

        self.session.execute_prepared(self.insert_stmt, {
            "metric_name": metric_name,
            "bucket": (bucket - datetime(1970, 1, 1).date()).days,
            "timestamp": timestamp,
            "value": value,
            "tags": tags or {},
            "ttl": ttl_seconds
        })

    def insert_batch(self, metrics):
        """Efficiently insert multiple metrics"""
        # Group by bucket for optimal batching
        by_bucket = {}

        for metric_name, value, tags in metrics:
            now = datetime.utcnow()
            bucket = now.date()
            bucket_days = (bucket - datetime(1970, 1, 1).date()).days

            if bucket_days not in by_bucket:
                by_bucket[bucket_days] = []

            by_bucket[bucket_days].append({
                "metric_name": metric_name,
                "bucket": bucket_days,
                "timestamp": int(now.timestamp() * 1000),
                "value": value,
                "tags": tags or {},
                "ttl": 86400
            })

        # Execute batches per bucket
        for bucket_days, bucket_metrics in by_bucket.items():
            batch = Batch("unlogged")
            for _ in bucket_metrics:
                batch.append_prepared(self.insert_stmt)

            self.session.batch(batch, bucket_metrics)

    def query_range(self, metric_name, start_time, end_time):
        """Query metrics in time range"""
        # Calculate buckets to query
        start_date = start_time.date()
        end_date = end_time.date()

        all_results = []
        current_date = start_date

        while current_date <= end_date:
            bucket_days = (current_date - datetime(1970, 1, 1).date()).days

            result = self.session.execute("""
                SELECT timestamp, value, tags
                FROM metrics
                WHERE metric_name = ?
                AND bucket = ?
                AND timestamp >= ?
                AND timestamp <= ?
            """, {
                "metric_name": metric_name,
                "bucket": bucket_days,
                "timestamp": int(start_time.timestamp() * 1000),
                "timestamp": int(end_time.timestamp() * 1000)
            })

            all_results.extend(result.rows())
            current_date += timedelta(days=1)

        return all_results

# Usage
session = Session.connect(["localhost:9042"])
session.use_keyspace("monitoring", False)

ts_store = TimeSeriesStore(session)

# Insert single metric
ts_store.insert_metric("cpu.usage", 45.2, {"host": "server1", "region": "us-east"})

# Insert batch
metrics = [
    ("cpu.usage", 45.2, {"host": "server1"}),
    ("mem.usage", 78.5, {"host": "server1"}),
    ("disk.usage", 62.1, {"host": "server1"}),
]
ts_store.insert_batch(metrics)

# Query time range
start = datetime.utcnow() - timedelta(hours=1)
end = datetime.utcnow()
results = ts_store.query_range("cpu.usage", start, end)

for row in results:
    timestamp, value, tags = row.columns()
    print(f"{timestamp}: {value} - {tags}")
```

## 3. Event Sourcing

```python
from rsylla import Session, Query
import json
import uuid

class EventStore:
    """Event sourcing implementation"""

    def __init__(self, session):
        self.session = session
        self._setup_schema()

    def _setup_schema(self):
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS events (
                aggregate_id uuid,
                version int,
                event_type text,
                event_data text,
                timestamp timestamp,
                PRIMARY KEY (aggregate_id, version)
            ) WITH CLUSTERING ORDER BY (version ASC)
        """)

        self.session.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                aggregate_id uuid PRIMARY KEY,
                version int,
                state text,
                timestamp timestamp
            )
        """)

        self.append_event_stmt = self.session.prepare("""
            INSERT INTO events (aggregate_id, version, event_type, event_data, timestamp)
            VALUES (?, ?, ?, ?, ?)
            IF NOT EXISTS
        """)

    def append_event(self, aggregate_id, version, event_type, event_data):
        """Append event with optimistic locking"""
        import time

        result = self.session.execute_prepared(self.append_event_stmt, {
            "aggregate_id": aggregate_id,
            "version": version,
            "event_type": event_type,
            "event_data": json.dumps(event_data),
            "timestamp": int(time.time() * 1000)
        })

        # Check if event was applied (LWT)
        row = result.first_row()
        if row and row[0]:  # [applied] column
            return True
        else:
            raise Exception(f"Version conflict for {aggregate_id} at version {version}")

    def get_events(self, aggregate_id, from_version=0):
        """Get all events for an aggregate"""
        result = self.session.execute("""
            SELECT version, event_type, event_data, timestamp
            FROM events
            WHERE aggregate_id = ?
            AND version >= ?
        """, {"aggregate_id": aggregate_id, "version": from_version})

        events = []
        for row in result:
            version, event_type, event_data, timestamp = row.columns()
            events.append({
                "version": version,
                "type": event_type,
                "data": json.loads(event_data),
                "timestamp": timestamp
            })

        return events

    def rebuild_aggregate(self, aggregate_id):
        """Rebuild aggregate state from events"""
        events = self.get_events(aggregate_id)

        # Apply events to rebuild state
        state = {}
        for event in events:
            state = self._apply_event(state, event)

        return state

    def _apply_event(self, state, event):
        """Apply event to state (domain-specific)"""
        # Example: account aggregate
        if event["type"] == "AccountCreated":
            state["balance"] = event["data"]["initial_balance"]
            state["owner"] = event["data"]["owner"]
        elif event["type"] == "MoneyDeposited":
            state["balance"] = state.get("balance", 0) + event["data"]["amount"]
        elif event["type"] == "MoneyWithdrawn":
            state["balance"] = state.get("balance", 0) - event["data"]["amount"]

        return state

    def create_snapshot(self, aggregate_id, version, state):
        """Create snapshot for faster loading"""
        import time

        self.session.execute("""
            INSERT INTO snapshots (aggregate_id, version, state, timestamp)
            VALUES (?, ?, ?, ?)
        """, {
            "aggregate_id": aggregate_id,
            "version": version,
            "state": json.dumps(state),
            "timestamp": int(time.time() * 1000)
        })

# Usage
session = Session.connect(["localhost:9042"])
session.use_keyspace("event_store", False)

store = EventStore(session)

# Create account
account_id = str(uuid.uuid4())
store.append_event(account_id, 1, "AccountCreated", {
    "owner": "Alice",
    "initial_balance": 1000.0
})

# Deposit money
store.append_event(account_id, 2, "MoneyDeposited", {
    "amount": 500.0
})

# Withdraw money
store.append_event(account_id, 3, "MoneyWithdrawn", {
    "amount": 200.0
})

# Rebuild state
state = store.rebuild_aggregate(account_id)
print(f"Account balance: {state['balance']}")  # 1300.0
```

## 4. Materialized Views Pattern

```python
from rsylla import Session, Batch

class MaterializedViewManager:
    """Manage denormalized views"""

    def __init__(self, session):
        self.session = session
        self._setup_schema()

    def _setup_schema(self):
        # Main table
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id uuid PRIMARY KEY,
                author_id int,
                title text,
                content text,
                tags set<text>,
                created_at timestamp
            )
        """)

        # View by author
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS posts_by_author (
                author_id int,
                created_at timestamp,
                post_id uuid,
                title text,
                PRIMARY KEY (author_id, created_at, post_id)
            ) WITH CLUSTERING ORDER BY (created_at DESC)
        """)

        # View by tag
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS posts_by_tag (
                tag text,
                created_at timestamp,
                post_id uuid,
                title text,
                author_id int,
                PRIMARY KEY (tag, created_at, post_id)
            ) WITH CLUSTERING ORDER BY (created_at DESC)
        """)

    def create_post(self, post_id, author_id, title, content, tags):
        """Create post and update all views atomically"""
        import time
        created_at = int(time.time() * 1000)

        # Create batch for atomic updates
        batch = Batch("logged")

        # Insert into main table
        batch.append_statement("""
            INSERT INTO posts (post_id, author_id, title, content, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """)

        # Update author view
        batch.append_statement("""
            INSERT INTO posts_by_author (author_id, created_at, post_id, title)
            VALUES (?, ?, ?, ?)
        """)

        # Update tag views
        values = [
            {
                "post_id": post_id,
                "author_id": author_id,
                "title": title,
                "content": content,
                "tags": tags,
                "created_at": created_at
            },
            {
                "author_id": author_id,
                "created_at": created_at,
                "post_id": post_id,
                "title": title
            }
        ]

        # Add statement for each tag
        for tag in tags:
            batch.append_statement("""
                INSERT INTO posts_by_tag (tag, created_at, post_id, title, author_id)
                VALUES (?, ?, ?, ?, ?)
            """)
            values.append({
                "tag": tag,
                "created_at": created_at,
                "post_id": post_id,
                "title": title,
                "author_id": author_id
            })

        # Execute batch
        self.session.batch(batch, values)

    def get_posts_by_author(self, author_id, limit=10):
        """Get posts by author"""
        result = self.session.execute("""
            SELECT post_id, title, created_at
            FROM posts_by_author
            WHERE author_id = ?
            LIMIT ?
        """, {"author_id": author_id, "limit": limit})

        return result.rows()

    def get_posts_by_tag(self, tag, limit=10):
        """Get posts by tag"""
        result = self.session.execute("""
            SELECT post_id, title, author_id, created_at
            FROM posts_by_tag
            WHERE tag = ?
            LIMIT ?
        """, {"tag": tag, "limit": limit})

        return result.rows()

# Usage
session = Session.connect(["localhost:9042"])
session.use_keyspace("blog", False)

manager = MaterializedViewManager(session)

# Create post (updates all views atomically)
import uuid
post_id = uuid.uuid4()
manager.create_post(
    post_id=post_id,
    author_id=123,
    title="My First Post",
    content="This is the content...",
    tags=["python", "database", "scylla"]
)

# Query by author
author_posts = manager.get_posts_by_author(123)
for row in author_posts:
    print(f"Post: {row[1]}")

# Query by tag
python_posts = manager.get_posts_by_tag("python")
for row in python_posts:
    print(f"Post: {row[1]} by {row[2]}")
```

## 5. Caching Layer

```python
from rsylla import Session
from datetime import datetime, timedelta

class CacheLayer:
    """Two-level cache with ScyllaDB"""

    def __init__(self, session):
        self.session = session
        self._memory_cache = {}
        self._setup_schema()

    def _setup_schema(self):
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key text PRIMARY KEY,
                value blob,
                created_at timestamp
            )
        """)

        self.get_stmt = self.session.prepare(
            "SELECT value FROM cache WHERE key = ?"
        ).set_idempotent(True)

        self.set_stmt = self.session.prepare(
            "INSERT INTO cache (key, value, created_at) VALUES (?, ?, ?) USING TTL ?"
        )

    def get(self, key):
        """Get value from cache (memory -> scylla)"""
        # Check memory cache first
        if key in self._memory_cache:
            value, expiry = self._memory_cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del self._memory_cache[key]

        # Check ScyllaDB
        result = self.session.execute_prepared(self.get_stmt, {"key": key})
        row = result.first_row()

        if row:
            value = row[0]
            # Update memory cache
            self._memory_cache[key] = (value, datetime.now() + timedelta(minutes=5))
            return value

        return None

    def set(self, key, value, ttl_seconds=3600):
        """Set value in cache"""
        import time
        import pickle

        # Serialize value
        serialized = pickle.dumps(value)

        # Store in ScyllaDB with TTL
        self.session.execute_prepared(self.set_stmt, {
            "key": key,
            "value": serialized,
            "created_at": int(time.time() * 1000),
            "ttl": ttl_seconds
        })

        # Update memory cache
        self._memory_cache[key] = (
            value,
            datetime.now() + timedelta(seconds=min(ttl_seconds, 300))
        )

    def delete(self, key):
        """Delete from cache"""
        self.session.execute(
            "DELETE FROM cache WHERE key = ?",
            {"key": key}
        )

        if key in self._memory_cache:
            del self._memory_cache[key]

# Usage
session = Session.connect(["localhost:9042"])
session.use_keyspace("cache", False)

cache = CacheLayer(session)

# Set value
cache.set("user:123", {"name": "Alice", "email": "alice@example.com"}, ttl_seconds=3600)

# Get value (from memory cache on second call)
user_data = cache.get("user:123")
print(user_data)

# Delete
cache.delete("user:123")
```

## 6. Rate Limiting

```python
from rsylla import Session
import time

class RateLimiter:
    """Token bucket rate limiter using ScyllaDB counters"""

    def __init__(self, session):
        self.session = session
        self._setup_schema()

    def _setup_schema(self):
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                identifier text,
                bucket_time bigint,
                tokens counter,
                PRIMARY KEY (identifier, bucket_time)
            )
        """)

        self.session.execute("""
            CREATE TABLE IF NOT EXISTS rate_limit_config (
                identifier text PRIMARY KEY,
                max_tokens int,
                refill_rate int,
                bucket_size_seconds int
            )
        """)

    def configure(self, identifier, max_tokens, refill_rate, bucket_size_seconds=60):
        """Configure rate limit for identifier"""
        self.session.execute("""
            INSERT INTO rate_limit_config
            (identifier, max_tokens, refill_rate, bucket_size_seconds)
            VALUES (?, ?, ?, ?)
        """, {
            "identifier": identifier,
            "max_tokens": max_tokens,
            "refill_rate": refill_rate,
            "bucket_size_seconds": bucket_size_seconds
        })

    def check_rate_limit(self, identifier, tokens_needed=1):
        """Check if request is allowed"""
        # Get configuration
        config_result = self.session.execute("""
            SELECT max_tokens, bucket_size_seconds
            FROM rate_limit_config
            WHERE identifier = ?
        """, {"identifier": identifier})

        config = config_result.first_row()
        if not config:
            return True  # No limit configured

        max_tokens, bucket_size = config.columns()

        # Calculate current bucket
        current_time = int(time.time())
        bucket_time = (current_time // bucket_size) * bucket_size

        # Get current token count
        count_result = self.session.execute("""
            SELECT tokens
            FROM rate_limits
            WHERE identifier = ?
            AND bucket_time = ?
        """, {"identifier": identifier, "bucket_time": bucket_time})

        current_tokens = 0
        row = count_result.first_row()
        if row:
            current_tokens = row[0]

        if current_tokens + tokens_needed <= max_tokens:
            # Allow request and increment counter
            self.session.execute("""
                UPDATE rate_limits
                SET tokens = tokens + ?
                WHERE identifier = ?
                AND bucket_time = ?
            """, {
                "tokens": tokens_needed,
                "identifier": identifier,
                "bucket_time": bucket_time
            })
            return True
        else:
            return False  # Rate limit exceeded

# Usage
session = Session.connect(["localhost:9042"])
session.use_keyspace("rate_limiting", False)

limiter = RateLimiter(session)

# Configure: max 100 requests per 60 seconds
limiter.configure("api:user:123", max_tokens=100, refill_rate=100, bucket_size_seconds=60)

# Check rate limit
if limiter.check_rate_limit("api:user:123"):
    print("Request allowed")
    # Process request
else:
    print("Rate limit exceeded")
    # Return 429 error
```

These patterns demonstrate real-world use cases and show how to effectively use rsylla for complex applications.
