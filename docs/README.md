# rscylla Documentation

Complete documentation for rscylla - Python bindings for ScyllaDB using the scylla-rust-driver.

## Quick Links

- [Project README](../README.md) - Main project information
- [Quick Start Guide](../QUICKSTART.md) - Get started quickly
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

## Documentation Structure

### Tutorials

Step-by-step guides for learning rscylla:

- **[Getting Started](tutorials/getting-started.md)** - Learn the basics of rscylla
  - Connecting to ScyllaDB
  - Creating keyspaces and tables
  - Basic CRUD operations
  - Using prepared statements
  - Complete example application

### API Reference

Detailed API documentation for all classes and methods:

- **[Session API](api/session.md)** - Session and SessionBuilder
  - Creating and configuring sessions
  - Connection management
  - Executing queries
  - Keyspace operations

- **[Query API](api/query.md)** - Query and PreparedStatement
  - Creating queries
  - Configuring execution options
  - Consistency levels
  - Prepared statements
  - Idempotency and tracing

- **[Results API](api/results.md)** - QueryResult and Row
  - Accessing query results
  - Iterating rows
  - Type conversions
  - Result metadata

- **[Batch API](api/batch.md)** - Batch operations
  - Creating batches
  - Batch types (logged, unlogged, counter)
  - Atomic operations
  - Best practices

### Guides

In-depth guides on specific topics:

- **[Data Types](guides/data-types.md)** - Working with CQL data types
  - Basic types (int, text, boolean, etc.)
  - Temporal types (timestamp, date, time)
  - Collection types (list, set, map)
  - Advanced types (uuid, counter, tuple, UDT)
  - Type conversion between Python and CQL
  - NULL handling

- **[Best Practices](guides/best-practices.md)** - Production-ready patterns
  - Connection management
  - Query optimization
  - Data modeling
  - Batch operations
  - Error handling
  - Performance optimization
  - Anti-patterns to avoid
  - Production checklist

### Examples

Real-world examples and patterns:

- **[Advanced Patterns](examples/advanced-patterns.md)** - Complex use cases
  - Multi-tenant applications
  - Time series data
  - Event sourcing
  - Materialized views pattern
  - Caching layer
  - Rate limiting

- **[Basic Examples](../examples/)** - Code examples
  - [basic_usage.py](../examples/basic_usage.py) - Simple CRUD operations
  - [prepared_statements.py](../examples/prepared_statements.py) - Using prepared statements
  - [batch_operations.py](../examples/batch_operations.py) - Batch operations
  - [advanced_configuration.py](../examples/advanced_configuration.py) - Advanced session configuration

## Documentation by Topic

### For Beginners

1. Start with [Quick Start Guide](../QUICKSTART.md)
2. Follow [Getting Started Tutorial](tutorials/getting-started.md)
3. Run the [basic examples](../examples/basic_usage.py)
4. Read [Data Types Guide](guides/data-types.md)

### For Development

1. Review [API Reference](api/session.md)
2. Study [Best Practices](guides/best-practices.md)
3. Explore [Advanced Patterns](examples/advanced-patterns.md)

### For Production

1. Read [Best Practices - Production Checklist](guides/best-practices.md#production-checklist)
2. Review [Connection Management](guides/best-practices.md#connection-management)
3. Study [Error Handling](guides/best-practices.md#error-handling)
4. Implement [Performance Optimization](guides/best-practices.md#performance-optimization)

## Common Tasks

### Connecting to ScyllaDB

```python
from rscylla import Session

session = Session.connect(["127.0.0.1:9042"])
```

See: [Session API](api/session.md#static-methods)

### Executing Queries

```python
result = session.execute(
    "SELECT * FROM users WHERE id = ?",
    {"id": 123}
)
```

See: [Session.execute()](api/session.md#executequery-str-values-optionaldictstr-any--none---queryresult)

### Using Prepared Statements

```python
prepared = session.prepare("INSERT INTO users (...) VALUES (...)")
session.execute_prepared(prepared, values)
```

See: [PreparedStatement](api/query.md#preparedstatement)

### Batch Operations

```python
from rscylla import Batch

batch = Batch("logged")
batch.append_statement("INSERT INTO ...")
session.batch(batch, values)
```

See: [Batch API](api/batch.md)

### Working with Results

```python
result = session.execute("SELECT * FROM users")

for row in result:
    print(row.columns())
```

See: [Results API](api/results.md)

## Feature Matrix

| Feature | Supported | Documentation |
|---------|-----------|---------------|
| Session Management | ✅ | [Session API](api/session.md) |
| Simple Queries | ✅ | [Session.execute()](api/session.md#instance-methods) |
| Prepared Statements | ✅ | [PreparedStatement](api/query.md#preparedstatement) |
| Batch Operations | ✅ | [Batch API](api/batch.md) |
| Consistency Levels | ✅ | [Query Configuration](api/query.md#with_consistencyconsistency-str---query) |
| Paging | ✅ | [Query.with_page_size()](api/query.md#with_page_sizepage_size-int---query) |
| Tracing | ✅ | [Query.with_tracing()](api/query.md#with_tracingtracing-bool---query) |
| Compression | ✅ | [SessionBuilder](api/session.md#compressioncompression-optionalstr---sessionbuilder) |
| Authentication | ✅ | [SessionBuilder.user()](api/session.md#userusername-str-password-str---sessionbuilder) |
| TTL | ✅ | [Data Types](guides/data-types.md) |
| Counters | ✅ | [Counter Type](guides/data-types.md#counter) |
| Collections | ✅ | [Collection Types](guides/data-types.md#collection-types) |
| UDT | ✅ | [User Defined Types](guides/data-types.md#user-defined-types-udt) |
| LWT (IF/IF NOT EXISTS) | ✅ | [Query](api/query.md) |
| All CQL Data Types | ✅ | [Data Types Guide](guides/data-types.md) |

## Getting Help

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/yourusername/rscylla/issues)
- **Discussions**: Ask questions on [GitHub Discussions](https://github.com/yourusername/rscylla/discussions)
- **ScyllaDB Docs**: [ScyllaDB Documentation](https://docs.scylladb.com/)
- **CQL Reference**: [CQL Documentation](https://cassandra.apache.org/doc/latest/cql/)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to rscylla.

## Related Resources

- [scylla-rust-driver](https://github.com/scylladb/scylla-rust-driver) - The underlying Rust driver
- [PyO3](https://pyo3.rs/) - Rust bindings for Python
- [ScyllaDB](https://www.scylladb.com/) - High-performance NoSQL database
- [Apache Cassandra](https://cassandra.apache.org/) - Original database compatible with ScyllaDB

## Version History

- **v0.1.0** - Initial release
  - Core functionality
  - Session management
  - Query execution
  - Prepared statements
  - Batch operations
  - Full type support

## License

This project is dual-licensed under MIT or Apache-2.0. See [LICENSE](../LICENSE) for details.
