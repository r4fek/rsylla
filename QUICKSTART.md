# Quick Start Guide for rsylla

## Prerequisites

Before building rsylla, ensure you have the following installed:

1. **Rust** (latest stable version)
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source $HOME/.cargo/env
   ```

2. **Python 3.8+**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

3. **Maturin** (PyO3 build tool)
   ```bash
   pip install maturin
   ```

## Building the Library

### Development Build

For development and testing:

```bash
# Build and install in development mode (editable install)
maturin develop

# Or with optimizations
maturin develop --release
```

### Production Build

For production use:

```bash
# Build wheel package
maturin build --release

# Install the built wheel
pip install target/wheels/*.whl
```

### Using the Makefile

```bash
# Development install
make develop

# Production build
make build

# Run tests
make test

# Format code
make fmt

# Run all examples
make examples
```

## Testing Your Installation

After building, test the installation:

```python
import rsylla

# Check version
print(rsylla.__version__)

# Verify imports work
from rsylla import Session, SessionBuilder, Query, PreparedStatement
print("rsylla installed successfully!")
```

## Running Examples

Make sure you have a running ScyllaDB or Cassandra instance on localhost:9042, then:

```bash
# Basic usage
python examples/basic_usage.py

# Prepared statements
python examples/prepared_statements.py

# Batch operations
python examples/batch_operations.py

# Advanced configuration
python examples/advanced_configuration.py
```

## Setting up ScyllaDB for Testing

### Using Docker

```bash
# Start ScyllaDB
docker run --name scylla -d -p 9042:9042 scylladb/scylla

# Wait for it to be ready (may take a minute)
docker logs -f scylla

# Stop ScyllaDB
docker stop scylla

# Remove container
docker rm scylla
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3'
services:
  scylla:
    image: scylladb/scylla
    ports:
      - "9042:9042"
    volumes:
      - scylla-data:/var/lib/scylla
volumes:
  scylla-data:
```

Then run:

```bash
docker-compose up -d
```

## First Program

Create `test_rsylla.py`:

```python
from rsylla import Session

# Connect to ScyllaDB
session = Session.connect(["127.0.0.1:9042"])

# Create a keyspace
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS test
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
""")

# Use the keyspace
session.use_keyspace("test", False)

# Create a table
session.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id int PRIMARY KEY,
        name text,
        email text
    )
""")

# Insert data
session.execute(
    "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
    {"id": 1, "name": "Alice", "email": "alice@example.com"}
)

# Query data
result = session.execute("SELECT * FROM users")
for row in result:
    print(row.columns())

print("Success!")
```

Run it:

```bash
python test_rsylla.py
```

## Troubleshooting

### Import Error

If you get `ImportError: No module named '_rsylla'`:
- Make sure you ran `maturin develop` or installed the wheel
- Check that you're using the correct Python environment

### Connection Error

If you get connection errors:
- Verify ScyllaDB/Cassandra is running: `docker ps`
- Check the port is correct: `netstat -an | grep 9042`
- Try connecting with cqlsh: `docker exec -it scylla cqlsh`

### Build Errors

If you get build errors:
- Update Rust: `rustup update`
- Update maturin: `pip install -U maturin`
- Clear cargo cache: `cargo clean`

## Next Steps

- Read the [README.md](README.md) for full API documentation
- Explore the [examples/](examples/) directory
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines

## Performance Tips

1. Use prepared statements for repeated queries
2. Enable compression for large data transfers
3. Use batch operations for multiple writes
4. Configure appropriate pool sizes
5. Use LOCAL_QUORUM for better latency in multi-DC setups

## Additional Resources

- [ScyllaDB Documentation](https://docs.scylladb.com/)
- [scylla-rust-driver](https://github.com/scylladb/scylla-rust-driver)
- [PyO3 Documentation](https://pyo3.rs/)
