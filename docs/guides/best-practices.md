# Best Practices Guide

This guide covers best practices for using rsylla efficiently and correctly.

## Connection Management

### Use Connection Pooling

```python
# ✅ DO: Create one session and reuse it
from rsylla import SessionBuilder

session = (
    SessionBuilder()
    .known_nodes(["node1:9042", "node2:9042", "node3:9042"])
    .pool_size(20)  # Pool size per host
    .build()
)

# Reuse session throughout application
def get_user(user_id):
    return session.execute("SELECT * FROM users WHERE id = ?", {"id": user_id})

def create_user(user_data):
    return session.execute("INSERT INTO users (...) VALUES (...)", user_data)
```

```python
# ❌ DON'T: Create new session for each query
def get_user(user_id):
    session = Session.connect(["localhost:9042"])  # SLOW!
    return session.execute("SELECT * FROM users WHERE id = ?", {"id": user_id})
```

### Configure Appropriately

```python
# Production configuration
session = (
    SessionBuilder()
    .known_nodes([
        "node1.prod.example.com:9042",
        "node2.prod.example.com:9042",
        "node3.prod.example.com:9042"
    ])
    .user("app_user", "secure_password")
    .pool_size(20)  # Depends on load
    .connection_timeout(10000)  # 10 seconds
    .compression("lz4")  # Reduce network traffic
    .tcp_nodelay(True)  # Low latency
    .tcp_keepalive(60000)  # Keep connections alive
    .build()
)
```

## Query Optimization

### Use Prepared Statements

```python
# ✅ DO: Prepare once, execute many times
prepared = session.prepare(
    "INSERT INTO users (id, name, email) VALUES (?, ?, ?)"
)

for i in range(1000):
    session.execute_prepared(prepared, {
        "id": i,
        "name": f"user{i}",
        "email": f"user{i}@example.com"
    })
```

```python
# ❌ DON'T: Parse same query repeatedly
for i in range(1000):
    session.execute(
        "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
        {"id": i, "name": f"user{i}", "email": f"user{i}@example.com"}
    )  # Query parsed 1000 times!
```

### Use Appropriate Consistency Levels

```python
from rsylla import Query

# Read queries: prefer lower consistency for better performance
read_query = (
    Query("SELECT * FROM users WHERE id = ?")
    .with_consistency("LOCAL_ONE")  # Fast reads
)

# Write queries: use QUORUM for durability
write_query = (
    Query("INSERT INTO users (...) VALUES (...)")
    .with_consistency("LOCAL_QUORUM")  # Durable writes
)

# Critical writes: use higher consistency
critical_write = (
    Query("INSERT INTO transactions (...) VALUES (...)")
    .with_consistency("QUORUM")  # Strong consistency
)
```

### Avoid SELECT *

```python
# ✅ DO: Select only needed columns
result = session.execute(
    "SELECT id, name, email FROM users WHERE id = ?",
    {"id": 1}
)

# ❌ DON'T: Select all columns when not needed
result = session.execute(
    "SELECT * FROM users WHERE id = ?",  # Might have 50+ columns
    {"id": 1}
)
```

## Data Modeling

### Partition Key Design

```python
# ✅ DO: Distribute data evenly
session.execute("""
    CREATE TABLE user_events (
        user_id int,
        event_date date,
        event_time timestamp,
        event_type text,
        PRIMARY KEY ((user_id, event_date), event_time)
    )
""")
# Good: Data distributed by user_id AND date

# ❌ DON'T: Create hot partitions
session.execute("""
    CREATE TABLE bad_events (
        event_date date,  -- Only a few dates -> hot partitions!
        event_time timestamp,
        user_id int,
        PRIMARY KEY (event_date, event_time)
    )
""")
```

### Denormalization

```python
# ✅ DO: Denormalize for read performance
session.execute("""
    CREATE TABLE users_by_id (
        user_id int PRIMARY KEY,
        username text,
        email text
    )
""")

session.execute("""
    CREATE TABLE users_by_email (
        email text PRIMARY KEY,
        user_id int,
        username text
    )
""")

# Two tables, but fast lookups by either id or email

# ❌ DON'T: Try to normalize like SQL
# This forces ALLOW FILTERING or secondary indexes (slow!)
```

### Use Static Columns Wisely

```python
# ✅ DO: Use static columns for partition-level data
session.execute("""
    CREATE TABLE user_posts (
        user_id int,
        post_id int,
        user_name text STATIC,  -- Same for all posts of user
        post_title text,
        PRIMARY KEY (user_id, post_id)
    )
""")
```

## Batch Operations

### Use Batches Correctly

```python
from rsylla import Batch

# ✅ DO: Batch statements for same partition
user_id = 123
batch = Batch("logged")
batch.append_statement("INSERT INTO user_posts (user_id, post_id, title) VALUES (?, ?, ?)")
batch.append_statement("UPDATE user_stats SET post_count = post_count + 1 WHERE user_id = ?")

session.batch(batch, [
    {"user_id": user_id, "post_id": 1, "title": "Post 1"},
    {"user_id": user_id}
])
# Good: Both statements for same user_id
```

```python
# ❌ DON'T: Batch across many partitions
batch = Batch("logged")
for user_id in range(1000):  # 1000 different partitions!
    batch.append_statement("UPDATE users SET login_count = login_count + 1 WHERE id = ?")

# This defeats the purpose and is slower than individual writes
```

### Choose Right Batch Type

```python
# Logged batch: atomicity required
logged_batch = Batch("logged")
logged_batch.append_statement("INSERT INTO accounts (id, balance) VALUES (?, ?)")
logged_batch.append_statement("INSERT INTO transactions (id, amount) VALUES (?, ?)")
# Both succeed or both fail

# Unlogged batch: independent statements, better performance
unlogged_batch = Batch("unlogged")
unlogged_batch.append_statement("INSERT INTO logs (id, message) VALUES (?, ?)")
unlogged_batch.append_statement("INSERT INTO logs (id, message) VALUES (?, ?)")
# Don't care if one fails

# Counter batch: counter updates only
counter_batch = Batch("counter")
counter_batch.append_statement("UPDATE stats SET views = views + ? WHERE page = ?")
```

## Error Handling

### Handle Errors Gracefully

```python
from rsylla import ScyllaError
import time

def execute_with_retry(session, query, values, max_retries=3):
    """Execute query with retry logic"""
    for attempt in range(max_retries):
        try:
            return session.execute(query, values)
        except ScyllaError as e:
            if attempt == max_retries - 1:
                raise
            print(f"Query failed (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(2 ** attempt)  # Exponential backoff

# Usage
result = execute_with_retry(
    session,
    "SELECT * FROM users WHERE id = ?",
    {"id": 1}
)
```

### Validate Results

```python
# ✅ DO: Check if results exist
result = session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
row = result.first_row()

if row:
    # Process row
    user_data = row.columns()
else:
    # Handle not found
    print("User not found")

# ✅ DO: Use single_row() when expecting exactly one row
try:
    row = result.single_row()
    # Process row
except ValueError:
    # Handle error (zero or multiple rows)
    print("Expected exactly one row")
```

## Performance Optimization

### Enable Compression

```python
# ✅ DO: Enable compression for large data transfers
session = (
    SessionBuilder()
    .known_nodes(["localhost:9042"])
    .compression("lz4")  # Or "snappy"
    .build()
)
```

### Use Pagination

```python
from rsylla import Query

# ✅ DO: Use paging for large result sets
query = (
    Query("SELECT * FROM large_table")
    .with_page_size(1000)  # Fetch 1000 rows at a time
)

result = session.query(query)

# Process results incrementally
for row in result:  # Automatically handles paging
    process_row(row)
```

```python
# ❌ DON'T: Load entire large table at once
result = session.execute("SELECT * FROM large_table")  # Could be millions of rows!
all_rows = result.rows()  # Out of memory!
```

### Configure Idempotency

```python
# ✅ DO: Mark idempotent queries for safe retries
query = (
    Query("SELECT * FROM users WHERE id = ?")
    .set_idempotent(True)  # Safe to retry
)

prepared = session.prepare("INSERT INTO logs (...) VALUES (...)")
prepared = prepared.set_idempotent(True)  # Safe to retry
```

### Use Tracing Selectively

```python
# ✅ DO: Enable tracing only when debugging
if DEBUG:
    query = query.with_tracing(True)

result = session.query(query)

if result.tracing_id():
    print(f"Trace ID: {result.tracing_id()}")
    # Query system_traces for details

# ❌ DON'T: Enable tracing in production
# Tracing has performance overhead
```

## Schema Design

### Use Appropriate Primary Keys

```python
# ✅ DO: Design for your queries
# Query: "Get all posts by user"
session.execute("""
    CREATE TABLE posts_by_user (
        user_id int,
        post_id int,
        title text,
        PRIMARY KEY (user_id, post_id)
    )
""")

# Query: "Get all posts in time range"
session.execute("""
    CREATE TABLE posts_by_time (
        day date,
        created_at timestamp,
        post_id int,
        title text,
        PRIMARY KEY (day, created_at)
    )
""")
```

### Avoid Large Partitions

```python
# ✅ DO: Limit partition size
session.execute("""
    CREATE TABLE user_events (
        user_id int,
        event_date date,  -- Include date in partition key
        event_time timestamp,
        event_data text,
        PRIMARY KEY ((user_id, event_date), event_time)
    )
""")
# Partition size limited to one day of events per user

# ❌ DON'T: Create unbounded partitions
session.execute("""
    CREATE TABLE user_events_bad (
        user_id int,
        event_time timestamp,
        event_data text,
        PRIMARY KEY (user_id, event_time)
    )
""")
# All events for user in single partition (could grow forever!)
```

### Use TTL for Temporary Data

```python
# ✅ DO: Use TTL for time-limited data
session.execute(
    "INSERT INTO sessions (session_id, data) VALUES (?, ?) USING TTL ?",
    {
        "session_id": "abc123",
        "data": "session data",
        "ttl": 3600  # 1 hour
    }
)

# Data automatically deleted after 1 hour
```

## Anti-Patterns to Avoid

### 1. ALLOW FILTERING

```python
# ❌ NEVER: Use ALLOW FILTERING in production
result = session.execute(
    "SELECT * FROM users WHERE email = ? ALLOW FILTERING",
    {"email": "alice@example.com"}
)
# This scans entire table! Very slow!

# ✅ DO: Create proper table structure
session.execute("""
    CREATE TABLE users_by_email (
        email text PRIMARY KEY,
        user_id int,
        name text
    )
""")
```

### 2. Secondary Indexes

```python
# ❌ AVOID: Secondary indexes (usually)
session.execute("CREATE INDEX ON users (email)")
# Secondary indexes have limitations and performance issues

# ✅ DO: Create denormalized table
session.execute("""
    CREATE TABLE users_by_email (
        email text PRIMARY KEY,
        user_id int
    )
""")
```

### 3. SELECT IN Queries

```python
# ❌ AVOID: Large IN queries
ids = list(range(1000))
result = session.execute(
    f"SELECT * FROM users WHERE id IN ({','.join('?' * len(ids))})",
    {"id": id for id in ids}
)

# ✅ DO: Execute individual queries (can be parallelized)
for user_id in ids:
    result = session.execute(
        "SELECT * FROM users WHERE id = ?",
        {"id": user_id}
    )
```

### 4. SELECT COUNT(*)

```python
# ❌ AVOID: COUNT(*) on large tables
result = session.execute("SELECT COUNT(*) FROM users")
# Very slow! Scans entire table

# ✅ DO: Maintain counters
session.execute("""
    CREATE TABLE user_count (
        type text PRIMARY KEY,
        count counter
    )
""")

# Increment on insert
session.execute(
    "UPDATE user_count SET count = count + 1 WHERE type = ?",
    {"type": "total"}
)
```

## Production Checklist

### Configuration

- [ ] Use connection pooling
- [ ] Configure appropriate pool size (10-20 per host typical)
- [ ] Enable compression (lz4 or snappy)
- [ ] Set connection timeout
- [ ] Enable TCP keepalive
- [ ] Use TCP nodelay

### Queries

- [ ] Use prepared statements for repeated queries
- [ ] Set appropriate consistency levels
- [ ] Enable idempotency where applicable
- [ ] Use pagination for large result sets
- [ ] Select only needed columns

### Error Handling

- [ ] Implement retry logic
- [ ] Handle connection failures
- [ ] Validate query results
- [ ] Log errors appropriately

### Monitoring

- [ ] Monitor query latency
- [ ] Track error rates
- [ ] Monitor connection pool usage
- [ ] Set up alerts for failures

### Schema

- [ ] Avoid large partitions
- [ ] Use appropriate data types
- [ ] Implement proper primary keys
- [ ] Use TTL for temporary data
- [ ] Document schema decisions

## Example: Complete Production Code

```python
from rsylla import SessionBuilder, Query, ScyllaError
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, nodes, keyspace, username=None, password=None):
        builder = (
            SessionBuilder()
            .known_nodes(nodes)
            .use_keyspace(keyspace, case_sensitive=False)
            .pool_size(20)
            .connection_timeout(10000)
            .compression("lz4")
            .tcp_nodelay(True)
            .tcp_keepalive(60000)
        )

        if username and password:
            builder = builder.user(username, password)

        self.session = builder.build()

        # Prepare frequently-used statements
        self._prepare_statements()

    def _prepare_statements(self):
        self.get_user_stmt = self.session.prepare(
            "SELECT id, name, email FROM users WHERE id = ?"
        ).with_consistency("LOCAL_ONE").set_idempotent(True)

        self.create_user_stmt = self.session.prepare(
            "INSERT INTO users (id, name, email, created_at) VALUES (?, ?, ?, ?)"
        ).with_consistency("LOCAL_QUORUM")

    def get_user(self, user_id, retries=3):
        """Get user with retry logic"""
        for attempt in range(retries):
            try:
                result = self.session.execute_prepared(
                    self.get_user_stmt,
                    {"id": user_id}
                )
                return result.first_row()
            except ScyllaError as e:
                if attempt == retries - 1:
                    logger.error(f"Failed to get user {user_id}: {e}")
                    raise
                logger.warning(f"Retry {attempt + 1} for user {user_id}")
                time.sleep(2 ** attempt)

    def create_user(self, user_id, name, email):
        """Create user with error handling"""
        try:
            current_time = int(time.time() * 1000)
            self.session.execute_prepared(
                self.create_user_stmt,
                {
                    "id": user_id,
                    "name": name,
                    "email": email,
                    "created_at": current_time
                }
            )
            logger.info(f"Created user {user_id}")
            return True
        except ScyllaError as e:
            logger.error(f"Failed to create user: {e}")
            return False

# Usage
db = Database(
    nodes=["node1:9042", "node2:9042"],
    keyspace="production",
    username="app_user",
    password="secure_password"
)

# Get user
user = db.get_user(123)
if user:
    print(f"User: {user.columns()}")

# Create user
success = db.create_user(456, "Bob", "bob@example.com")
```
