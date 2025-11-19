# Session API Reference

The `Session` class is the main entry point for interacting with ScyllaDB/Cassandra clusters.

## SessionBuilder

### Overview

`SessionBuilder` provides a fluent interface for configuring and creating `Session` instances.

### Constructor

```python
builder = SessionBuilder()
```

Creates a new session builder with default configuration.

### Methods

#### `known_node(hostname: str) -> SessionBuilder`

Adds a known node to connect to.

**Parameters:**
- `hostname`: Node address in format `"host:port"` or just `"host"` (defaults to port 9042)

**Returns:** Self for method chaining

**Example:**
```python
builder = SessionBuilder().known_node("127.0.0.1:9042")
```

#### `known_nodes(hostnames: List[str]) -> SessionBuilder`

Adds multiple known nodes.

**Parameters:**
- `hostnames`: List of node addresses

**Returns:** Self for method chaining

**Example:**
```python
builder = SessionBuilder().known_nodes([
    "node1.example.com:9042",
    "node2.example.com:9042",
    "node3.example.com:9042"
])
```

#### `use_keyspace(keyspace_name: str, case_sensitive: bool) -> SessionBuilder`

Sets the default keyspace for the session.

**Parameters:**
- `keyspace_name`: Name of the keyspace
- `case_sensitive`: Whether the keyspace name is case-sensitive

**Returns:** Self for method chaining

**Example:**
```python
builder = SessionBuilder().use_keyspace("my_keyspace", case_sensitive=False)
```

#### `connection_timeout(duration_ms: int) -> SessionBuilder`

Sets the connection timeout in milliseconds.

**Parameters:**
- `duration_ms`: Timeout in milliseconds

**Returns:** Self for method chaining

**Example:**
```python
builder = SessionBuilder().connection_timeout(5000)  # 5 seconds
```

#### `pool_size(size: int) -> SessionBuilder`

Sets the connection pool size per host.

**Parameters:**
- `size`: Number of connections per host

**Returns:** Self for method chaining

**Example:**
```python
builder = SessionBuilder().pool_size(10)
```

#### `user(username: str, password: str) -> SessionBuilder`

Sets authentication credentials.

**Parameters:**
- `username`: Username for authentication
- `password`: Password for authentication

**Returns:** Self for method chaining

**Example:**
```python
builder = SessionBuilder().user("cassandra", "cassandra")
```

#### `compression(compression: Optional[str]) -> SessionBuilder`

Sets the compression algorithm.

**Parameters:**
- `compression`: Compression type - `"lz4"`, `"snappy"`, or `None`

**Returns:** Self for method chaining

**Example:**
```python
builder = SessionBuilder().compression("lz4")
```

#### `tcp_nodelay(nodelay: bool) -> SessionBuilder`

Enables or disables TCP_NODELAY (Nagle's algorithm).

**Parameters:**
- `nodelay`: True to disable Nagle's algorithm (recommended)

**Returns:** Self for method chaining

**Example:**
```python
builder = SessionBuilder().tcp_nodelay(True)
```

#### `tcp_keepalive(keepalive_ms: Optional[int]) -> SessionBuilder`

Sets TCP keepalive interval.

**Parameters:**
- `keepalive_ms`: Keepalive interval in milliseconds, or None to disable

**Returns:** Self for method chaining

**Example:**
```python
builder = SessionBuilder().tcp_keepalive(60000)  # 60 seconds
```

#### `build() -> Session`

Builds and returns a configured Session.

**Returns:** Configured Session instance

**Raises:** `ScyllaError` if connection fails

**Example:**
```python
session = SessionBuilder().known_nodes(["127.0.0.1:9042"]).build()
```

### Complete Example

```python
from rscylla import SessionBuilder

session = (
    SessionBuilder()
    .known_nodes([
        "10.0.0.1:9042",
        "10.0.0.2:9042",
        "10.0.0.3:9042"
    ])
    .user("myuser", "mypassword")
    .use_keyspace("production", case_sensitive=False)
    .connection_timeout(10000)
    .pool_size(20)
    .compression("lz4")
    .tcp_nodelay(True)
    .tcp_keepalive(60000)
    .build()
)
```

---

## Session

### Overview

`Session` represents an active connection to a ScyllaDB/Cassandra cluster.

### Static Methods

#### `connect(nodes: List[str]) -> Session`

Quick way to create a session with default configuration.

**Parameters:**
- `nodes`: List of node addresses

**Returns:** Session instance

**Raises:** `ScyllaError` if connection fails

**Example:**
```python
from rscylla import Session

session = Session.connect(["127.0.0.1:9042"])
```

### Instance Methods

#### `execute(query: str, values: Optional[Dict[str, Any]] = None) -> QueryResult`

Executes a CQL query string.

**Parameters:**
- `query`: CQL query string
- `values`: Optional dictionary of parameter values

**Returns:** QueryResult object

**Raises:** `ScyllaError` on query failure

**Examples:**

Simple query:
```python
result = session.execute("SELECT * FROM users")
```

Query with parameters:
```python
result = session.execute(
    "SELECT * FROM users WHERE id = ? AND status = ?",
    {"id": 123, "status": "active"}
)
```

DDL statement:
```python
session.execute("""
    CREATE TABLE users (
        id int PRIMARY KEY,
        name text,
        email text
    )
""")
```

#### `query(query: Query, values: Optional[Dict[str, Any]] = None) -> QueryResult`

Executes a Query object with configuration.

**Parameters:**
- `query`: Query object
- `values`: Optional dictionary of parameter values

**Returns:** QueryResult object

**Raises:** `ScyllaError` on query failure

**Example:**
```python
from rscylla import Query

query = (
    Query("SELECT * FROM users WHERE id = ?")
    .with_consistency("QUORUM")
    .with_page_size(100)
)

result = session.query(query, {"id": 123})
```

#### `prepare(query: str) -> PreparedStatement`

Prepares a query for efficient repeated execution.

**Parameters:**
- `query`: CQL query string with placeholders

**Returns:** PreparedStatement object

**Raises:** `ScyllaError` if preparation fails

**Example:**
```python
prepared = session.prepare(
    "INSERT INTO users (id, name, email) VALUES (?, ?, ?)"
)
```

#### `execute_prepared(prepared: PreparedStatement, values: Optional[Dict[str, Any]] = None) -> QueryResult`

Executes a prepared statement.

**Parameters:**
- `prepared`: PreparedStatement object
- `values`: Optional dictionary of parameter values

**Returns:** QueryResult object

**Raises:** `ScyllaError` on execution failure

**Example:**
```python
result = session.execute_prepared(
    prepared,
    {"id": 1, "name": "Alice", "email": "alice@example.com"}
)
```

#### `batch(batch: Batch, values: List[Dict[str, Any]]) -> QueryResult`

Executes a batch operation.

**Parameters:**
- `batch`: Batch object
- `values`: List of value dictionaries, one per statement

**Returns:** QueryResult object

**Raises:** `ScyllaError` on execution failure

**Example:**
```python
from rscylla import Batch

batch = Batch("logged")
batch.append_statement("INSERT INTO users (id, name) VALUES (?, ?)")
batch.append_statement("INSERT INTO users (id, name) VALUES (?, ?)")

session.batch(batch, [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
])
```

#### `use_keyspace(keyspace_name: str, case_sensitive: bool) -> None`

Changes the current keyspace.

**Parameters:**
- `keyspace_name`: Name of the keyspace
- `case_sensitive`: Whether the name is case-sensitive

**Raises:** `ScyllaError` if keyspace doesn't exist

**Example:**
```python
session.use_keyspace("production", case_sensitive=False)
```

#### `await_schema_agreement() -> bool`

Waits for schema agreement across the cluster.

**Returns:** True if agreement was reached

**Example:**
```python
session.execute("CREATE TABLE test (id int PRIMARY KEY)")
if session.await_schema_agreement():
    print("Schema synchronized across cluster")
```

#### `get_cluster_data() -> str`

Returns cluster metadata as a string.

**Returns:** String representation of cluster data

**Example:**
```python
cluster_info = session.get_cluster_data()
print(cluster_info)
```

#### `get_keyspace() -> Optional[str]`

Returns the current keyspace name.

**Returns:** Keyspace name or None

**Example:**
```python
current_ks = session.get_keyspace()
if current_ks:
    print(f"Using keyspace: {current_ks}")
```

### Complete Example

```python
from rscylla import Session, Query, Batch

# Create session
session = Session.connect(["127.0.0.1:9042"])

# Create keyspace
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS app
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
""")

# Use keyspace
session.use_keyspace("app", False)

# Create table
session.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id int PRIMARY KEY,
        name text,
        email text,
        created_at timestamp
    )
""")

# Wait for schema agreement
session.await_schema_agreement()

# Insert data
session.execute(
    "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
    {"id": 1, "name": "Alice", "email": "alice@example.com"}
)

# Query with options
query = Query("SELECT * FROM users WHERE id = ?").with_consistency("ONE")
result = session.query(query, {"id": 1})

for row in result:
    print(row.columns())

# Prepared statement
prepared = session.prepare("INSERT INTO users (id, name, email) VALUES (?, ?, ?)")
for i in range(10):
    session.execute_prepared(
        prepared,
        {"id": i, "name": f"User{i}", "email": f"user{i}@example.com"}
    )

# Batch operation
batch = Batch("logged")
batch.append_statement("UPDATE users SET name = ? WHERE id = ?")
batch.append_statement("UPDATE users SET name = ? WHERE id = ?")

session.batch(batch, [
    {"name": "Alice Updated", "id": 1},
    {"name": "Bob Updated", "id": 2}
])
```
