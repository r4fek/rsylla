# Benchmark Suite

This directory contains comprehensive benchmarks comparing `rsylla` with other Python drivers for ScyllaDB/Cassandra.

## Quick Start

### Prerequisites

1. **Running ScyllaDB or Cassandra instance**
   ```bash
   # Using Docker
   docker run --name scylla -p 9042:9042 -d scylladb/scylla
   ```

2. **Install required libraries**
   ```bash
   # Install rsylla (from this repository)
   pip install -e .

   # Install acsylla (optional, for comparison)
   pip install acsylla

   # Install cassandra-driver (optional, for comparison)
   pip install cassandra-driver
   ```

### Running Benchmarks

1. **Setup the database schema**
   ```bash
   python benchmark/setup_schema.py --host 127.0.0.1 --keyspace acsylla
   ```

2. **Run all benchmarks**
   ```bash
   python benchmark/run_all_benchmarks.py --concurrency 32 --duration 60
   ```

   This will:
   - Run benchmarks for rsylla, acsylla, and cassandra-driver
   - Generate a comprehensive markdown report: `benchmark_results.md`

3. **Run individual library benchmarks**
   ```bash
   # rsylla only
   python benchmark/rsylla_benchmark.py --concurrency 32 --duration 60

   # Or run specific libraries
   python benchmark/run_all_benchmarks.py --libraries rsylla acsylla
   ```

## Benchmark Options

```bash
python benchmark/run_all_benchmarks.py --help
```

Available options:
- `--concurrency N`: Number of concurrent clients (default: 32)
- `--duration N`: Duration of each benchmark in seconds (default: 10)
- `--host HOST`: ScyllaDB/Cassandra host (default: 127.0.0.1)
- `--keyspace KEYSPACE`: Keyspace name (default: acsylla)
- `--output FILE`: Output markdown file (default: benchmark_results.md)
- `--libraries LIB [LIB ...]`: Libraries to benchmark (choices: rsylla, acsylla, cassandra-driver)

## Benchmark Types

Each library is tested with the following operations:

### Write Operations
- **write**: Simple INSERT with string concatenation
- **write_bind**: INSERT with parameter binding
- **write_prepared**: INSERT using prepared statements

### Read Operations
- **read**: Simple SELECT with string concatenation
- **read_bind**: SELECT with parameter binding
- **read_prepared**: SELECT using prepared statements

## Understanding Results

The benchmark report includes:

1. **Operations per second (ops/sec)**: Higher is better
2. **Average latency**: Lower is better
3. **P90 latency**: 90th percentile latency
4. **P99 latency**: 99th percentile latency

## Files

- `rsylla_benchmark.py`: Benchmark implementation for rsylla
- `acsylla_benchmark.py`: Original acsylla benchmark (downloaded from acsylla repo)
- `cassandra_python_benchmark.py`: Benchmark for cassandra-driver (downloaded from acsylla repo)
- `run_all_benchmarks.py`: Unified runner that executes all benchmarks and generates comparison report
- `setup_schema.py`: Database schema setup script
- `README.md`: This file

## Tips for Accurate Benchmarks

1. **Use a dedicated test environment** - Don't run on production
2. **Run for sufficient duration** - At least 60 seconds per benchmark for stable results
3. **Consistent load** - Keep system load consistent during benchmarks
4. **Multiple runs** - Run benchmarks multiple times and average results
5. **Warm-up** - The first run may be slower due to cold caches

## Example Output

```
SUMMARY - rsylla
================================================================================
write                          |      45000 ops/sec | avg: 0.000712s | p90: 0.001234s | p99: 0.002456s
write_bind                     |      42000 ops/sec | avg: 0.000762s | p90: 0.001312s | p99: 0.002678s
write_prepared                 |      48000 ops/sec | avg: 0.000667s | p90: 0.001145s | p99: 0.002234s
read                           |      52000 ops/sec | avg: 0.000615s | p90: 0.001089s | p99: 0.002123s
read_bind                      |      49000 ops/sec | avg: 0.000653s | p90: 0.001156s | p99: 0.002267s
read_prepared                  |      55000 ops/sec | avg: 0.000582s | p90: 0.001023s | p99: 0.002001s
```

## Troubleshooting

### Connection Issues
```
Error: Could not connect to ScyllaDB/Cassandra
```
Solution: Ensure ScyllaDB/Cassandra is running and accessible at the specified host/port

### Schema Issues
```
Error: Keyspace 'acsylla' does not exist
```
Solution: Run the setup script first: `python benchmark/setup_schema.py`

### Library Not Found
```
ModuleNotFoundError: No module named 'acsylla'
```
Solution: Install the required library: `pip install acsylla`

## Contributing

To add new benchmark scenarios:

1. Add the test function to the respective benchmark file
2. Register it in the `main()` function
3. Update this README with the new benchmark description
