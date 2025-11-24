# ScyllaDB/Cassandra Python Driver Benchmark Comparison

**Generated:** 2025-11-24 12:32:28

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
| rsylla | 27,768 | 🏆 |

**read_bind:**

| Library | Ops/sec | Winner |
|---------|---------|--------|
| rsylla | 18,930 | 🏆 |

**read_prepared:**

| Library | Ops/sec | Winner |
|---------|---------|--------|
| rsylla | 30,272 | 🏆 |

**write:**

| Library | Ops/sec | Winner |
|---------|---------|--------|
| rsylla | 29,497 | 🏆 |

**write_bind:**

| Library | Ops/sec | Winner |
|---------|---------|--------|
| rsylla | 20,022 | 🏆 |

**write_prepared:**

| Library | Ops/sec | Winner |
|---------|---------|--------|
| rsylla | 31,443 | 🏆 |


## Detailed Results

### read

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 27,768 | 0.001151 | 0.001573 | 0.002408 |

### read_bind

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 18,930 | 0.001688 | 0.002292 | 0.004375 |

### read_prepared

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 30,272 | 0.001055 | 0.001463 | 0.002137 |

### write

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 29,497 | 0.001083 | 0.001457 | 0.002205 |

### write_bind

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 20,022 | 0.001596 | 0.002105 | 0.004217 |

### write_prepared

| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |
|---------|---------|-----------------|-----------------|------------------|
| rsylla | 31,443 | 0.001016 | 0.001394 | 0.002056 |

## Performance Analysis

### Throughput Comparison

Relative performance (ops/sec) normalized to cassandra-driver baseline:

| Benchmark | rsylla | acsylla | cassandra-driver |
|-----------|--------|---------|------------------|

### Latency Comparison

Average latency comparison (lower is better):

| Benchmark | rsylla (ms) | acsylla (ms) | cassandra-driver (ms) |
|-----------|-------------|--------------|------------------------|
| read | 1.151 | N/A | N/A |
| read_bind | 1.688 | N/A | N/A |
| read_prepared | 1.055 | N/A | N/A |
| write | 1.083 | N/A | N/A |
| write_bind | 1.596 | N/A | N/A |
| write_prepared | 1.016 | N/A | N/A |

## Key Findings


## Recommendations

### When to use rsylla:
- Maximum throughput is required
- Modern async/await Python code
- Building on official ScyllaDB Rust driver
- Full type safety and IDE support needed

### When to use acsylla:
- Async/await support required
- Good balance of performance and maturity
- Existing acsylla codebase

### When to use cassandra-driver:
- Maximum compatibility with existing code
- Synchronous/thread-based architecture preferred
- Official DataStax support required
- Mature ecosystem and extensive documentation

## Raw Benchmark Data

```json
{
  "rsylla": [
    {
      "name": "write",
      "ops_per_sec": 29497,
      "avg": 0.001083,
      "p90": 0.001457,
      "p99": 0.002205
    },
    {
      "name": "write_bind",
      "ops_per_sec": 20022,
      "avg": 0.001596,
      "p90": 0.002105,
      "p99": 0.004217
    },
    {
      "name": "write_prepared",
      "ops_per_sec": 31443,
      "avg": 0.001016,
      "p90": 0.001394,
      "p99": 0.002056
    },
    {
      "name": "read",
      "ops_per_sec": 27768,
      "avg": 0.001151,
      "p90": 0.001573,
      "p99": 0.002408
    },
    {
      "name": "read_bind",
      "ops_per_sec": 18930,
      "avg": 0.001688,
      "p90": 0.002292,
      "p99": 0.004375
    },
    {
      "name": "read_prepared",
      "ops_per_sec": 30272,
      "avg": 0.001055,
      "p90": 0.001463,
      "p99": 0.002137
    }
  ]
}
```
