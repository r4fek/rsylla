# rsylla Test Suite

This directory contains comprehensive tests for rsylla.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_session.py          # Session and SessionBuilder tests
├── test_query.py            # Query execution tests
├── test_prepared.py         # PreparedStatement tests
├── test_batch.py            # Batch operation tests
├── test_results.py          # QueryResult and Row tests
└── test_datatypes.py        # Data type conversion tests
```

## Running Tests

### Quick Start

Run all tests with automatic setup:

```bash
./run_tests.sh
```

Or using make:

```bash
make test
```

### Manual Setup

1. **Start ScyllaDB**:
   ```bash
   docker compose up -d
   ```

2. **Wait for ScyllaDB to be ready** (about 30-60 seconds):
   ```bash
   docker compose logs -f scylla
   # Wait for "Scylla version" message
   ```

3. **Build the library**:
   ```bash
   maturin develop
   ```

4. **Install test requirements**:
   ```bash
   pip install -r requirements-test.txt
   ```

5. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

### Test Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_session.py -v

# Run specific test
pytest tests/test_session.py::TestSession::test_use_keyspace -v

# Run with detailed output
pytest tests/ -vv --tb=long

# Run tests in parallel (faster)
pytest tests/ -n auto
```

## Test Categories

Tests are marked with pytest markers:

- `@pytest.mark.integration` - Tests requiring ScyllaDB

Run specific categories:

```bash
# Run only integration tests
pytest tests/ -m integration -v
```

## Test Fixtures

### Session Fixtures

- `scylla_host` - ScyllaDB host (default: 127.0.0.1)
- `scylla_port` - ScyllaDB port (default: 9042)
- `scylla_connection_string` - Full connection string
- `wait_for_scylla` - Waits for ScyllaDB to be ready
- `session` - Shared session for all tests

### Data Fixtures

- `test_keyspace` - Creates a test keyspace (function-scoped)
- `users_table` - Creates a users table
- `sample_users` - Inserts sample user data

## Test Coverage

The test suite covers:

### Core Functionality (90+ tests)

1. **Session Management**
   - Connection creation
   - SessionBuilder configuration
   - Keyspace operations
   - Schema agreement

2. **Query Execution**
   - Simple queries
   - Parameterized queries
   - DDL operations (CREATE, DROP)
   - DML operations (INSERT, UPDATE, DELETE)

3. **Prepared Statements**
   - Statement preparation
   - Execution with parameters
   - Batch execution
   - Statement metadata

4. **Batch Operations**
   - Logged batches
   - Unlogged batches
   - Counter batches
   - Mixed statement types

5. **Result Handling**
   - Row iteration
   - Result metadata
   - Type conversions
   - Empty results

6. **Data Types**
   - Integer types (int, bigint)
   - Floating point (float, double)
   - Text types (text, varchar)
   - Boolean
   - Blob (binary data)
   - Timestamp
   - Collections (list, set, map)
   - Counter
   - NULL values

## Environment Variables

Configure tests using environment variables:

```bash
# Set custom ScyllaDB host
export SCYLLA_HOST=192.168.1.100

# Set custom port
export SCYLLA_PORT=9042

# Run tests
pytest tests/ -v
```

## Troubleshooting

### ScyllaDB not ready

If tests fail with connection errors:

```bash
# Check if ScyllaDB is running
docker compose ps

# Check ScyllaDB logs
docker compose logs scylla

# Wait longer for ScyllaDB to start
sleep 60

# Try connecting manually
docker compose exec scylla cqlsh -e "describe cluster"
```

### Library not built

If you get import errors:

```bash
# Build the library
maturin develop

# Verify import works
python -c "import rsylla; print('OK')"
```

### Docker issues

```bash
# Stop all containers
docker compose down -v

# Remove volumes
docker volume prune

# Start fresh
docker compose up -d
```

### Test failures

```bash
# Run with more verbose output
pytest tests/test_session.py -vv --tb=long

# Run single failing test
pytest tests/test_session.py::TestSession::test_use_keyspace -vv

# Show print statements
pytest tests/ -v -s
```

## Writing New Tests

### Example Test

```python
import pytest
from rsylla import Session

@pytest.mark.integration
class TestMyFeature:
    """Test my new feature"""

    def test_my_feature(self, session, test_keyspace):
        """Test description"""
        # Setup
        session.execute("CREATE TABLE test (id int PRIMARY KEY)")

        # Execute
        session.execute("INSERT INTO test (id) VALUES (?)", {"id": 1})

        # Verify
        result = session.execute("SELECT * FROM test WHERE id = ?", {"id": 1})
        assert len(result) == 1

        # Cleanup happens automatically via fixtures
```

### Best Practices

1. Use fixtures for setup/teardown
2. Mark integration tests with `@pytest.mark.integration`
3. Use descriptive test names
4. Test both success and failure cases
5. Clean up resources (fixtures handle this)
6. Keep tests independent

## Continuous Integration

Tests can be run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Start ScyllaDB
  run: docker compose up -d

- name: Wait for ScyllaDB
  run: sleep 60

- name: Build library
  run: maturin develop

- name: Run tests
  run: pytest tests/ -v
```

## Performance

Test suite execution time:

- Full suite: ~2-3 minutes
- Individual test file: ~10-30 seconds
- Single test: ~1-5 seconds

Most time is spent waiting for ScyllaDB to process operations.

## Cleanup

Stop ScyllaDB and cleanup:

```bash
# Stop containers
docker compose down

# Remove volumes
docker compose down -v

# Remove all test data
make clean
```
