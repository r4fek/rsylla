# Query API Reference

## Query

### Overview

`Query` represents a CQL query with configurable execution options.

### Constructor

```python
query = Query(query_string)
```

**Parameters:**
- `query_string`: CQL query string

**Example:**
```python
from rscylla import Query

query = Query("SELECT * FROM users WHERE id = ?")
```

### Methods

#### `with_consistency(consistency: str) -> Query`

Sets the consistency level for the query.

**Parameters:**
- `consistency`: Consistency level name

**Valid Values:**
- `"ANY"` - Write to at least one node
- `"ONE"` - Read/write one replica
- `"TWO"` - Read/write two replicas
- `"THREE"` - Read/write three replicas
- `"QUORUM"` - Read/write quorum of replicas
- `"ALL"` - Read/write all replicas
- `"LOCAL_QUORUM"` - Quorum in local datacenter
- `"EACH_QUORUM"` - Quorum in each datacenter
- `"LOCAL_ONE"` - One replica in local datacenter

**Returns:** Self for method chaining

**Example:**
```python
query = Query("SELECT * FROM users").with_consistency("QUORUM")
```

#### `with_serial_consistency(serial_consistency: str) -> Query`

Sets the serial consistency for lightweight transactions.

**Parameters:**
- `serial_consistency`: Serial consistency level

**Valid Values:**
- `"SERIAL"` - Serial consistency across all datacenters
- `"LOCAL_SERIAL"` - Serial consistency in local datacenter

**Returns:** Self for method chaining

**Example:**
```python
query = (
    Query("INSERT INTO users (id, name) VALUES (?, ?) IF NOT EXISTS")
    .with_serial_consistency("LOCAL_SERIAL")
)
```

#### `with_page_size(page_size: int) -> Query`

Sets the page size for result pagination.

**Parameters:**
- `page_size`: Number of rows per page

**Returns:** Self for method chaining

**Example:**
```python
query = Query("SELECT * FROM large_table").with_page_size(1000)
```

#### `with_timestamp(timestamp: int) -> Query`

Sets the timestamp for the query (in microseconds).

**Parameters:**
- `timestamp`: Timestamp in microseconds since epoch

**Returns:** Self for method chaining

**Example:**
```python
import time

timestamp_micros = int(time.time() * 1000000)
query = (
    Query("INSERT INTO events (id, data) VALUES (?, ?)")
    .with_timestamp(timestamp_micros)
)
```

#### `with_timeout(timeout_ms: int) -> Query`

Sets the request timeout.

**Parameters:**
- `timeout_ms`: Timeout in milliseconds

**Returns:** Self for method chaining

**Example:**
```python
query = Query("SELECT * FROM users").with_timeout(5000)  # 5 seconds
```

#### `with_tracing(tracing: bool) -> Query`

Enables or disables query tracing.

**Parameters:**
- `tracing`: True to enable tracing

**Returns:** Self for method chaining

**Example:**
```python
query = Query("SELECT * FROM users").with_tracing(True)

result = session.query(query)
if result.tracing_id():
    print(f"Trace ID: {result.tracing_id()}")
```

#### `is_idempotent() -> bool`

Checks if the query is marked as idempotent.

**Returns:** True if idempotent

**Example:**
```python
if query.is_idempotent():
    print("Query can be safely retried")
```

#### `set_idempotent(idempotent: bool) -> None`

Sets whether the query is idempotent.

**Parameters:**
- `idempotent`: True if query is idempotent

**Example:**
```python
query = Query("SELECT * FROM users")
query.set_idempotent(True)
```

#### `get_contents() -> str`

Returns the query string.

**Returns:** CQL query string

**Example:**
```python
query_str = query.get_contents()
print(f"Executing: {query_str}")
```

### Complete Examples

#### Read Query with Options

```python
from rscylla import Session, Query

session = Session.connect(["127.0.0.1:9042"])
session.use_keyspace("myapp", False)

# Configure read query
query = (
    Query("SELECT * FROM users WHERE status = ?")
    .with_consistency("LOCAL_QUORUM")
    .with_page_size(100)
    .with_timeout(10000)
    .with_tracing(True)
)

query.set_idempotent(True)

result = session.query(query, {"status": "active"})

print(f"Found {len(result)} users")
if result.tracing_id():
    print(f"Trace: {result.tracing_id()}")
```

#### Write Query with Timestamp

```python
import time
from rscylla import Query

# Create query with custom timestamp
timestamp = int(time.time() * 1000000)

query = (
    Query("INSERT INTO events (id, timestamp, data) VALUES (?, ?, ?)")
    .with_consistency("QUORUM")
    .with_timestamp(timestamp)
)

session.query(query, {
    "id": 123,
    "timestamp": timestamp // 1000,  # Convert to millis for column
    "data": "event data"
})
```

#### Conditional Write (LWT)

```python
# Lightweight transaction with serial consistency
query = (
    Query("UPDATE users SET balance = ? WHERE id = ? IF balance = ?")
    .with_consistency("QUORUM")
    .with_serial_consistency("SERIAL")
)

result = session.query(query, {
    "balance": 1000,
    "id": 123,
    "balance": 500  # Condition
})

# Check if conditional update succeeded
if result.first_row():
    applied = result.first_row()[0]  # [applied] column
    if applied:
        print("Update successful")
    else:
        print("Condition not met")
```

---

## PreparedStatement

### Overview

`PreparedStatement` represents a prepared query that can be executed multiple times efficiently.

### Creation

Prepared statements are created using `Session.prepare()`:

```python
prepared = session.prepare("INSERT INTO users (id, name, email) VALUES (?, ?, ?)")
```

### Methods

#### `with_consistency(consistency: str) -> PreparedStatement`

Sets the consistency level.

**Parameters:**
- `consistency`: Consistency level name (same as Query)

**Returns:** New PreparedStatement with updated configuration

**Example:**
```python
prepared = prepared.with_consistency("LOCAL_QUORUM")
```

#### `with_serial_consistency(serial_consistency: str) -> PreparedStatement`

Sets the serial consistency level.

**Parameters:**
- `serial_consistency`: Serial consistency level

**Returns:** New PreparedStatement with updated configuration

**Example:**
```python
prepared = prepared.with_serial_consistency("LOCAL_SERIAL")
```

#### `with_page_size(page_size: int) -> PreparedStatement`

Sets the page size.

**Parameters:**
- `page_size`: Number of rows per page

**Returns:** New PreparedStatement with updated configuration

**Example:**
```python
prepared = prepared.with_page_size(500)
```

#### `with_timestamp(timestamp: int) -> PreparedStatement`

Sets the timestamp.

**Parameters:**
- `timestamp`: Timestamp in microseconds

**Returns:** New PreparedStatement with updated configuration

**Example:**
```python
prepared = prepared.with_timestamp(int(time.time() * 1000000))
```

#### `with_tracing(tracing: bool) -> PreparedStatement`

Enables or disables tracing.

**Parameters:**
- `tracing`: True to enable tracing

**Returns:** New PreparedStatement with updated configuration

**Example:**
```python
prepared = prepared.with_tracing(True)
```

#### `is_idempotent() -> bool`

Checks if the statement is idempotent.

**Returns:** True if idempotent

#### `set_idempotent(idempotent: bool) -> PreparedStatement`

Sets idempotency.

**Parameters:**
- `idempotent`: True if idempotent

**Returns:** New PreparedStatement with updated configuration

**Example:**
```python
prepared = prepared.set_idempotent(True)
```

#### `get_id() -> bytes`

Returns the prepared statement ID.

**Returns:** Statement ID as bytes

**Example:**
```python
stmt_id = prepared.get_id()
print(f"Statement ID: {stmt_id.hex()}")
```

#### `get_statement() -> str`

Returns the query string.

**Returns:** CQL query string

**Example:**
```python
query_str = prepared.get_statement()
print(f"Prepared: {query_str}")
```

### Complete Examples

#### Efficient Bulk Insert

```python
from rscylla import Session

session = Session.connect(["127.0.0.1:9042"])
session.use_keyspace("myapp", False)

# Prepare once
prepared = session.prepare(
    "INSERT INTO products (id, name, price, quantity) VALUES (?, ?, ?, ?)"
)

# Configure for optimal performance
prepared = (
    prepared
    .with_consistency("ONE")
    .set_idempotent(True)
)

# Execute many times
products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "quantity": 10},
    {"id": 2, "name": "Mouse", "price": 29.99, "quantity": 100},
    {"id": 3, "name": "Keyboard", "price": 79.99, "quantity": 50},
    # ... thousands more
]

for product in products:
    session.execute_prepared(prepared, product)
```

#### Prepared Statement with TTL

```python
# Prepare statement with TTL
prepared = session.prepare(
    "INSERT INTO sessions (session_id, user_id, data) VALUES (?, ?, ?) USING TTL ?"
)

# Execute with 1 hour TTL
session.execute_prepared(prepared, {
    "session_id": "abc123",
    "user_id": 456,
    "data": "session data",
    "ttl": 3600  # 1 hour in seconds
})
```

#### Read with Prepared Statement

```python
# Prepare read query
prepared = session.prepare(
    "SELECT name, email, created_at FROM users WHERE id = ?"
)

# Configure
prepared = (
    prepared
    .with_consistency("LOCAL_ONE")
    .with_page_size(1)
    .set_idempotent(True)
)

# Execute multiple times
user_ids = [1, 2, 3, 4, 5]

for user_id in user_ids:
    result = session.execute_prepared(prepared, {"id": user_id})
    row = result.first_row()
    if row:
        name, email, created_at = row[0], row[1], row[2]
        print(f"User: {name} ({email})")
```

#### Reusing Prepared Statement Configuration

```python
# Base prepared statement
base_insert = session.prepare("INSERT INTO logs (id, timestamp, message) VALUES (?, ?, ?)")

# Create variants with different configurations
fast_insert = base_insert.with_consistency("ANY")
safe_insert = base_insert.with_consistency("QUORUM")
traced_insert = base_insert.with_tracing(True)

# Use appropriate variant
if urgent:
    session.execute_prepared(fast_insert, log_data)
elif critical:
    session.execute_prepared(safe_insert, log_data)
else:
    session.execute_prepared(traced_insert, log_data)
```
