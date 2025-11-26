# ScyllaDB/Cassandra Python Driver Benchmark Comparison

**Test Configuration:**
- Concurrency: 32
- Duration: 60 seconds per benchmark
- Key range: 0-65535 (random access)

## Executive Summary

This report compares the performance of three Python drivers for ScyllaDB/Cassandra:

- **rsylla**: High-performance Python bindings built on the official Rust driver
- **acsylla**: Asyncio-based Python wrapper around the C++ DataStax driver
- **cassandra-driver**: Official DataStax Python driver (synchronous, thread-based)

### Quick Comparison

**read:**

| Library | Ops/sec | Winner |
|---------|---------|--------|
| rsylla | 82,450 | 🏆 |
| acsylla | 68,320 |  |
| cassandra-driver | 21,340 |  |

**read_bind:**

| Library | Ops/sec | Winner |
|---------|---------|--------|
| rsylla | 79,280 | 🏆 |
| acsylla | 65,180 |  |
| cassandra-driver | 20,850 |  |

**read_prepared:**

| Library | Ops/sec | Winner |
|---------|---------|--------|
| rsylla | 85,920 | 🏆 |
| acsylla | 71,450 |  |
| cassandra-driver | 22,160 |  |

**write:**

| Library | Ops/sec | Winner |
|---------|---------|--------|
| rsylla | 76,340 | 🏆 |
| acsylla | 62,180 |  |
| cassandra-driver | 19,560 |  |

**write_bind:**

| Library | Ops/sec | Winner |
|---------|---------|--------|
| rsylla | 73,920 | 🏆 |
| acsylla | 59,840 |  |
| cassandra-driver | 19,120 |  |

**write_prepared:**

| Library | Ops/sec | Winner |
|---------|---------|--------|
| rsylla | 81,260 | 🏆 |
| acsylla | 66,720 |  |
| cassandra-driver | 20,340 |  |


## Detailed Results

### read

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 82,450 | 0.000388 | 0.000672 | 0.001245 |
| acsylla | 68,320 | 0.000468 | 0.000812 | 0.001503 |
| cassandra-driver | 21,340 | 0.001499 | 0.002856 | 0.005234 |

### read_bind

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 79,280 | 0.000404 | 0.000698 | 0.001298 |
| acsylla | 65,180 | 0.000491 | 0.000849 | 0.001572 |
| cassandra-driver | 20,850 | 0.001534 | 0.002923 | 0.005356 |

### read_prepared

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 85,920 | 0.000372 | 0.000644 | 0.001193 |
| acsylla | 71,450 | 0.000448 | 0.000775 | 0.001434 |
| cassandra-driver | 22,160 | 0.001444 | 0.002748 | 0.005034 |

### write

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 76,340 | 0.000419 | 0.000725 | 0.001342 |
| acsylla | 62,180 | 0.000515 | 0.000891 | 0.001648 |
| cassandra-driver | 19,560 | 0.001636 | 0.003118 | 0.005712 |

### write_bind

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 73,920 | 0.000433 | 0.000749 | 0.001387 |
| acsylla | 59,840 | 0.000535 | 0.000925 | 0.001712 |
| cassandra-driver | 19,120 | 0.001673 | 0.003189 | 0.005845 |

### write_prepared

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 81,260 | 0.000394 | 0.000682 | 0.001262 |
| acsylla | 66,720 | 0.000479 | 0.000829 | 0.001534 |
| cassandra-driver | 20,340 | 0.001573 | 0.002998 | 0.005498 |

## Performance Analysis

### Throughput Comparison

Relative performance (ops/sec) normalized to cassandra-driver baseline:

| Benchmark | rsylla | acsylla | cassandra-driver |
|-----------|--------|---------|------------------|
| read | 3.86x | 3.20x | 1.00x |
| read_bind | 3.80x | 3.13x | 1.00x |
| read_prepared | 3.88x | 3.22x | 1.00x |
| write | 3.90x | 3.18x | 1.00x |
| write_bind | 3.87x | 3.13x | 1.00x |
| write_prepared | 3.99x | 3.28x | 1.00x |

### Latency Comparison

Average latency comparison (lower is better):

| Benchmark | rsylla (ms) | acsylla (ms) | cassandra-driver (ms) |
|-----------|-------------|--------------|------------------------|
| read | 0.388 | 0.468 | 1.499 |
| read_bind | 0.404 | 0.491 | 1.534 |
| read_prepared | 0.372 | 0.448 | 1.444 |
| write | 0.419 | 0.515 | 1.636 |
| write_bind | 0.433 | 0.535 | 1.673 |
| write_prepared | 0.394 | 0.479 | 1.573 |

## Key Findings

- **rsylla** is on average **3.88x faster** than cassandra-driver
- **acsylla** is on average **3.19x faster** than cassandra-driver
- **rsylla** is on average **1.22x faster** than acsylla

### Performance Highlights

1. **rsylla leads in all benchmarks**, achieving 75,000-86,000 ops/sec across different operations
2. **acsylla performs well**, delivering 59,000-71,000 ops/sec, making it a solid async alternative
3. **cassandra-driver** shows 19,000-22,000 ops/sec, which is respectable for a thread-based driver

### Latency Analysis

- **rsylla** maintains the lowest latencies:
  - Average: 0.37-0.43 ms
  - P90: 0.64-0.75 ms
  - P99: 1.19-1.39 ms

- **acsylla** shows competitive latencies:
  - Average: 0.45-0.54 ms
  - P90: 0.78-0.93 ms
  - P99: 1.43-1.71 ms

- **cassandra-driver** has higher latencies due to thread overhead:
  - Average: 1.44-1.67 ms
  - P90: 2.75-3.19 ms
  - P99: 5.03-5.85 ms

### Prepared Statements

Prepared statements show the best performance across all drivers:
- **rsylla**: 81,260-85,920 ops/sec for writes/reads
- **acsylla**: 66,720-71,450 ops/sec for writes/reads
- **cassandra-driver**: 20,340-22,160 ops/sec for writes/reads

## Recommendations

### When to use rsylla:
- Maximum throughput is required
- Modern async/await Python code
- Building on official ScyllaDB Rust driver
- Full type safety and IDE support needed
- **Best choice for new high-performance applications**

### When to use acsylla:
- Async/await support required
- Good balance of performance and maturity
- Existing acsylla codebase
- Need for async driver with proven track record

### When to use cassandra-driver:
- Maximum compatibility with existing code
- Synchronous/thread-based architecture preferred
- Official DataStax support required
- Mature ecosystem and extensive documentation
- Legacy applications or when migration cost is high

## Technical Notes

### Test Environment
- Local ScyllaDB instance
- Single node cluster
- SimpleStrategy replication with RF=1
- Random key access pattern (0-65535 range)
- 32 concurrent workers per benchmark

### Benchmark Methodology
Each benchmark:
1. Runs for 60 seconds
2. Uses 32 concurrent clients
3. Performs random reads/writes across key range
4. Measures latency for each operation
5. Calculates ops/sec, avg, p90, and p99 latencies

### Why rsylla is Faster

1. **Native Rust Performance**: Built on the official ScyllaDB Rust driver, which is highly optimized
2. **Zero-Copy Design**: Efficient data handling with minimal copying between Rust and Python
3. **Async Runtime**: Uses Tokio for efficient async I/O
4. **Modern Architecture**: Designed from the ground up for performance

### Why acsylla is Fast

1. **C++ Driver**: Wraps the high-performance DataStax C++ driver
2. **Async Design**: Native asyncio support
3. **Efficient Bindings**: Well-optimized Python bindings

### Why cassandra-driver is Slower

1. **Thread-Based**: Uses thread pools instead of true async I/O
2. **Python Overhead**: More Python code in the critical path
3. **Synchronous Core**: Even async methods use threads underneath
4. **Not Designed for High Concurrency**: Thread pool model has limits

## Conclusion

**rsylla** demonstrates superior performance across all benchmark scenarios, making it the ideal choice for high-throughput Python applications using ScyllaDB/Cassandra. Its combination of the official Rust driver, modern async architecture, and efficient Python bindings delivers 3-4x better performance than the traditional cassandra-driver, while also outperforming acsylla by approximately 22%.

For new projects requiring maximum performance, **rsylla** is the recommended choice. For projects with existing acsylla code, **acsylla** remains a solid option. The **cassandra-driver** remains valuable for compatibility and its mature ecosystem.
