# Benchmark Quick Start Guide

This guide will help you run benchmarks comparing rsylla with acsylla and cassandra-driver.

## Prerequisites

### 1. Start ScyllaDB/Cassandra

Using Docker (recommended for testing):

```bash
# Start ScyllaDB
docker run --name scylla -p 9042:9042 -d scylladb/scylla

# Wait for it to be ready (check logs)
docker logs -f scylla
# Wait until you see "Starting listening for CQL clients"
# Press Ctrl+C to exit logs
```

Or using Docker Compose:

```bash
# In the rsylla project directory
docker-compose up -d

# Check status
docker-compose ps
```

### 2. Install Dependencies

```bash
# Make sure you're in the rsylla project directory
cd /path/to/rsylla

# Install rsylla in development mode
maturin develop --release

# Install comparison libraries (optional but recommended)
pip install acsylla cassandra-driver
```

## Running Benchmarks

### Step 1: Setup Database Schema

```bash
python benchmark/setup_schema.py
```

This creates:
- Keyspace: `acsylla` (with SimpleStrategy, RF=1)
- Table: `test` (id int PRIMARY KEY, value int)
- Initial test data (100 rows)

### Step 2: Run Benchmarks

#### Quick Test (10 seconds per benchmark)

```bash
python benchmark/run_all_benchmarks.py --duration 10
```

#### Full Benchmark (60 seconds per benchmark - recommended)

```bash
python benchmark/run_all_benchmarks.py --concurrency 32 --duration 60
```

#### Run Only rsylla vs acsylla

```bash
python benchmark/run_all_benchmarks.py --libraries rsylla acsylla --duration 30
```

#### Custom Configuration

```bash
python benchmark/run_all_benchmarks.py \
  --concurrency 64 \
  --duration 120 \
  --host 192.168.1.100 \
  --keyspace my_keyspace \
  --output my_results.md
```

### Step 3: View Results

The benchmark will generate a markdown report (default: `benchmark_results.md`):

```bash
# View in terminal
cat benchmark_results.md

# Or open in your editor
code benchmark_results.md
```

## Understanding the Output

During the benchmark run, you'll see output like:

```
================================================================================
Running benchmark/rsylla_benchmark.py...
================================================================================

Starting benchmark write
Tests results:
	Ops/sec: 76340
	Avg: 0.000419
	P90: 0.000725
	P99: 0.001342

Starting benchmark write_bind
Tests results:
	Ops/sec: 73920
	Avg: 0.000433
	P90: 0.000749
	P99: 0.001387
...
```

**Metrics explained:**
- **Ops/sec**: Operations per second (higher is better)
- **Avg**: Average latency in seconds (lower is better)
- **P90**: 90th percentile latency (lower is better)
- **P99**: 99th percentile latency (lower is better)

## Individual Library Benchmarks

You can also run benchmarks for individual libraries:

### rsylla Only

```bash
python benchmark/rsylla_benchmark.py --concurrency 32 --duration 60
```

### acsylla Only

```bash
python /tmp/acsylla_benchmark.py --concurrency 32 --duration 60
```

### cassandra-driver Only

```bash
python /tmp/cassandra_python_benchmark.py --concurrency 32 --duration 60
```

## Troubleshooting

### "Connection refused"

```
Error: Could not connect to ScyllaDB at 127.0.0.1:9042
```

**Solution**: Make sure ScyllaDB/Cassandra is running:
```bash
docker ps | grep scylla
# or
docker-compose ps
```

### "Keyspace does not exist"

```
Error: Keyspace 'acsylla' does not exist
```

**Solution**: Run the setup script:
```bash
python benchmark/setup_schema.py
```

### "Module not found: acsylla"

```
ModuleNotFoundError: No module named 'acsylla'
```

**Solution**: Install the library or run without it:
```bash
# Install it
pip install acsylla

# Or run without it
python benchmark/run_all_benchmarks.py --libraries rsylla cassandra-driver
```

### Low Performance Results

If results seem unusually low:

1. **Check system load**: Make sure no other heavy processes are running
2. **Use release build**: Always use `maturin develop --release`
3. **Longer duration**: Use at least 60 seconds for stable results
4. **Check ScyllaDB**: Ensure ScyllaDB is healthy and not overloaded

### Docker on Mac/Windows

If using Docker Desktop on Mac/Windows, network performance might be lower due to virtualization overhead. For best results, use native Linux or a Linux VM.

## Tips for Accurate Benchmarks

1. **Run multiple times**: Results can vary, average 3-5 runs
2. **Warm-up**: The first run might be slower (cold caches)
3. **Consistent environment**: Close unnecessary applications
4. **Longer duration**: 60+ seconds gives more stable results
5. **Watch resources**: Monitor CPU, memory, and network during tests

## Next Steps

After running benchmarks:

1. Review the generated markdown report
2. Compare throughput (ops/sec) and latency metrics
3. Check the "Key Findings" section for overall comparison
4. See the "Recommendations" section for guidance on which driver to use

## Example Results

See `BENCHMARK_RESULTS_EXAMPLE.md` for an example of what the output looks like with realistic performance numbers.

## Advanced Usage

### Custom Keyspace Setup

```bash
python benchmark/setup_schema.py \
  --host 192.168.1.100 \
  --keyspace my_bench \
  --replication-factor 3
```

### Benchmark Against Remote Cluster

```bash
python benchmark/run_all_benchmarks.py \
  --host production-cluster.example.com \
  --keyspace bench_test \
  --concurrency 128 \
  --duration 300
```

### Testing Different Concurrency Levels

```bash
for concurrency in 16 32 64 128; do
  python benchmark/run_all_benchmarks.py \
    --concurrency $concurrency \
    --duration 60 \
    --output "results_c${concurrency}.md"
done
```

## Questions?

Check the main README or open an issue on GitHub if you encounter problems.
