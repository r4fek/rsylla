# rsylla

**The fastest Python driver for ScyllaDB.** High-performance Python bindings using the official [scylla-rust-driver](https://github.com/scylladb/scylla-rust-driver).

## Performance

rsylla is **~3.9x faster** than the DataStax cassandra-driver and **~1.2x faster** than acsylla:

- **85,000+ ops/sec** for read/write operations
- **Sub-millisecond latencies** (0.37-0.43ms average)
- **Zero-copy design** for efficient data handling

**[See detailed benchmark results →](BENCHMARKS.md)**

## Features

- **Fastest Performance**: Built on top of the official Rust driver for ScyllaDB
- **Full API Coverage**: Every function/method from the Rust driver has a Python equivalent
- **Type Hints**: Complete type annotations for better IDE support
- **Async Runtime**: Efficient async operations handled by Tokio runtime
- **Easy to Use**: Pythonic API that feels natural

## Installation

```bash
pip install rsylla
```

### Building from source

You'll need [Rust](https://rustup.rs/) and [maturin](https://github.com/PyO3/maturin) installed:

```bash
# Install maturin
pip install maturin

# Build and install
maturin develop --release
```

## Quick Start

```python
import asyncio
from rsylla import Session

async def main():
    # Connect to ScyllaDB cluster
    session = await Session.connect(["127.0.0.1:9042"])

    # Execute a query
    result = await session.execute(
        "SELECT * FROM system.local WHERE key = ?",
        {"key": "local"}
    )

    # Iterate over rows
    for row in result:
        print(row.columns())

asyncio.run(main())
```

## Usage Examples

### Creating a Session

```python
import asyncio
from rsylla import SessionBuilder

async def main():
    # Using SessionBuilder for advanced configuration
    session = await (
        SessionBuilder()
        .known_nodes(["127.0.0.1:9042", "127.0.0.2:9042"])
        .user("username", "password")
        .use_keyspace("my_keyspace", case_sensitive=False)
        .connection_timeout(5000)  # 5 seconds
        .pool_size(10)
        .compression("lz4")
        .tcp_nodelay(True)
        .build()
    )

asyncio.run(main())
```

### Executing Queries

```python
import asyncio
from rsylla import Session

async def main():
    session = await Session.connect(["127.0.0.1:9042"])

    # Simple query
    result = await session.execute("SELECT * FROM users")

    # Query with parameters
    result = await session.execute(
        "SELECT * FROM users WHERE id = ?",
        {"id": 123}
    )

    # Get first row
    row = result.first_row()
    if row:
        print(row.columns())

    # Get single row (raises exception if not exactly one row)
    row = result.single_row()

    # Iterate over all rows
    for row in result:
        print(row[0], row[1], row[2])

asyncio.run(main())
```

### Using Query Objects

```python
import asyncio
from rsylla import Session, Query

async def main():
    session = await Session.connect(["127.0.0.1:9042"])

    # Create a query with configuration
    query = (
        Query("SELECT * FROM users WHERE id = ?")
        .with_consistency("QUORUM")
        .with_page_size(1000)
        .with_timeout(10000)
        .with_tracing(True)
    )

    result = await session.query(query, {"id": 123})

    # Check tracing info
    if result.tracing_id():
        print(f"Trace ID: {result.tracing_id()}")

asyncio.run(main())
```

### Prepared Statements

```python
import asyncio
from rsylla import Session

async def main():
    session = await Session.connect(["127.0.0.1:9042"])

    # Prepare a statement
    prepared = await session.prepare("INSERT INTO users (id, name, email) VALUES (?, ?, ?)")

    # Execute prepared statement
    result = await session.execute_prepared(
        prepared,
        {"id": 1, "name": "John Doe", "email": "john@example.com"}
    )

    # Prepared statements with configuration
    prepared = (
        prepared
        .with_consistency("LOCAL_QUORUM")
        .with_serial_consistency("SERIAL")
    )

    result = await session.execute_prepared(prepared, {"id": 2, "name": "Jane", "email": "jane@example.com"})

asyncio.run(main())
```

### Batch Operations

```python
import asyncio
from rsylla import Session, Batch

async def main():
    session = await Session.connect(["127.0.0.1:9042"])

    # Create a batch
    batch = Batch("logged")  # or "unlogged" or "counter"

    # Add statements to batch
    batch.append_statement("INSERT INTO users (id, name) VALUES (?, ?)")
    batch.append_statement("INSERT INTO users (id, name) VALUES (?, ?)")

    # Configure batch
    batch = (
        batch
        .with_consistency("QUORUM")
        .with_timestamp(1234567890)
    )

    # Execute batch with values for each statement
    result = await session.batch(
        batch,
        [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"}
        ]
    )

asyncio.run(main())
```

### Working with Results

```python
import asyncio
from rsylla import Session

async def main():
    session = await Session.connect(["127.0.0.1:9042"])
    result = await session.execute("SELECT * FROM users")

    # Get all rows
    rows = result.rows()
    print(f"Found {len(rows)} rows")

    # Get rows as dictionaries
    rows_dict = result.rows_typed()
    for row_dict in rows_dict:
        print(row_dict)

    # Get column specifications
    col_specs = result.col_specs()
    for spec in col_specs:
        print(f"Column: {spec['name']}, Type: {spec['typ']}")

    # Check for warnings
    if result.warnings():
        print("Warnings:", result.warnings())

    # Boolean check
    if result:
        print("Query returned rows")

asyncio.run(main())
```

### Keyspace Operations

```python
import asyncio
from rsylla import Session

async def main():
    session = await Session.connect(["127.0.0.1:9042"])

    # Change keyspace
    await session.use_keyspace("another_keyspace", case_sensitive=False)

    # Get current keyspace
    current_ks = session.get_keyspace()
    print(f"Current keyspace: {current_ks}")

    # Wait for schema agreement
    agreed = await session.await_schema_agreement()
    print(f"Schema agreement reached: {agreed}")

asyncio.run(main())
```

### Error Handling

```python
import asyncio
from rsylla import Session, ScyllaError

async def main():
    session = await Session.connect(["127.0.0.1:9042"])

    try:
        result = await session.execute("INVALID QUERY")
    except ScyllaError as e:
        print(f"Query error: {e}")

asyncio.run(main())
```

## Consistency Levels

The following consistency levels are supported:

- `ANY`
- `ONE`
- `TWO`
- `THREE`
- `QUORUM`
- `ALL`
- `LOCAL_QUORUM` (or `LOCALQUORUM`)
- `EACH_QUORUM` (or `EACHQUORUM`)
- `LOCAL_ONE` (or `LOCALONE`)

Serial consistency levels:

- `SERIAL`
- `LOCAL_SERIAL` (or `LOCALSERIAL`)

## Batch Types

- `logged` - Default, atomicity guaranteed
- `unlogged` - No atomicity guarantee, better performance
- `counter` - For counter updates

## Compression Types

- `lz4` - LZ4 compression
- `snappy` - Snappy compression
- `None` - No compression

## Type Mapping

Python types are automatically converted to CQL types:

| Python Type | CQL Type |
|------------|----------|
| `bool` | `boolean` |
| `int` | `int`, `bigint` |
| `float` | `float`, `double` |
| `str` | `text`, `varchar` |
| `bytes` | `blob` |
| `list` | `list` |
| `dict` | `map` |
| `None` | `NULL` |

## API Reference

### SessionBuilder

- `known_node(hostname: str)` - Add a known node
- `known_nodes(hostnames: List[str])` - Add multiple known nodes
- `use_keyspace(keyspace_name: str, case_sensitive: bool)` - Set default keyspace
- `connection_timeout(duration_ms: int)` - Set connection timeout
- `pool_size(size: int)` - Set connection pool size
- `user(username: str, password: str)` - Set authentication credentials
- `compression(compression: Optional[str])` - Set compression type
- `tcp_nodelay(nodelay: bool)` - Enable/disable TCP_NODELAY
- `tcp_keepalive(keepalive_ms: Optional[int])` - Set TCP keepalive
- `build()` - Build the session

### Session

- `connect(nodes: List[str])` - Create a session (static method)
- `execute(query: str, values: Optional[Dict[str, Any]])` - Execute a query
- `query(query: Query, values: Optional[Dict[str, Any]])` - Execute a Query object
- `prepare(query: str)` - Prepare a statement
- `execute_prepared(prepared: PreparedStatement, values: Optional[Dict[str, Any]])` - Execute prepared statement
- `batch(batch: Batch, values: List[Dict[str, Any]])` - Execute a batch
- `use_keyspace(keyspace_name: str, case_sensitive: bool)` - Change keyspace
- `await_schema_agreement()` - Wait for schema agreement
- `get_cluster_data()` - Get cluster metadata
- `get_keyspace()` - Get current keyspace

### Query

- `__init__(query: str)` - Create a query
- `with_consistency(consistency: str)` - Set consistency level
- `with_serial_consistency(serial_consistency: str)` - Set serial consistency
- `with_page_size(page_size: int)` - Set page size
- `with_timestamp(timestamp: int)` - Set timestamp
- `with_timeout(timeout_ms: int)` - Set timeout
- `with_tracing(tracing: bool)` - Enable/disable tracing
- `is_idempotent()` - Check if idempotent
- `set_idempotent(idempotent: bool)` - Set idempotency
- `get_contents()` - Get query string

### PreparedStatement

Similar methods to Query, plus:

- `get_id()` - Get prepared statement ID
- `get_statement()` - Get query string

### QueryResult

- `rows()` - Get all rows
- `first_row()` - Get first row or None
- `single_row()` - Get single row (raises exception if not exactly one)
- `first_row_typed()` - Get first row as dictionary
- `rows_typed()` - Get all rows as dictionaries
- `col_specs()` - Get column specifications
- `tracing_id()` - Get tracing ID
- `warnings()` - Get query warnings
- Supports iteration, `len()`, and boolean checks

### Row

- `columns()` - Get all column values
- `as_dict()` - Convert to dictionary
- `get(index: int)` - Get column by index
- Supports indexing with `[]` and `len()`

### Batch

- `__init__(batch_type: str)` - Create a batch
- `append_statement(query: str)` - Add a statement
- `append_query(query: Query)` - Add a Query object
- `append_prepared(prepared: PreparedStatement)` - Add a prepared statement
- `with_consistency(consistency: str)` - Set consistency level
- `with_serial_consistency(serial_consistency: str)` - Set serial consistency
- `with_timestamp(timestamp: int)` - Set timestamp
- `with_timeout(timeout_ms: int)` - Set timeout
- `with_tracing(tracing: bool)` - Enable/disable tracing
- `is_idempotent()` - Check if idempotent
- `set_idempotent(idempotent: bool)` - Set idempotency
- `statements_count()` - Get number of statements

## License

This project is dual-licensed under MIT or Apache-2.0, matching the scylla-rust-driver license.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [scylla-rust-driver](https://github.com/scylladb/scylla-rust-driver)
- [PyO3](https://github.com/PyO3/pyo3)
- [ScyllaDB](https://www.scylladb.com/)
