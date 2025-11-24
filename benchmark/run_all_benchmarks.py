#!/usr/bin/env python3
"""
Unified benchmark runner for comparing acsylla, cassandra-driver, and rsylla.

This script runs benchmarks for all three libraries and generates a comprehensive
comparison report in markdown format.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime


def run_benchmark(
    script: str, concurrency: int, duration: int, host: str, keyspace: str
) -> list[dict] | None:
    """Run a single benchmark script and capture results."""
    print(f"\n{'=' * 80}")
    print(f"Running {script}...")
    print(f"{'=' * 80}\n")

    try:
        result = subprocess.run(
            [
                sys.executable,
                script,
                "--concurrency",
                str(concurrency),
                "--duration",
                str(duration),
                "--host",
                host,
                "--keyspace",
                keyspace,
            ],
            capture_output=True,
            text=True,
            timeout=duration * 10,  # Generous timeout
        )

        if result.returncode != 0:
            print(f"Error running {script}:")
            print(result.stderr)
            return None

        print(result.stdout)
        return parse_output(result.stdout)

    except subprocess.TimeoutExpired:
        print(f"Timeout running {script}")
        return None
    except Exception as e:
        print(f"Exception running {script}: {e}")
        return None


def parse_output(output: str) -> list[dict]:
    """Parse benchmark output to extract metrics."""
    results = []
    lines = output.split("\n")

    current_benchmark = None
    for line in lines:
        if "Starting benchmark" in line:
            current_benchmark = line.split("Starting benchmark")[1].strip()
        elif "Ops/sec:" in line or "QPS:" in line:
            if current_benchmark:
                ops_per_sec = int(line.split(":")[1].strip())
        elif "Avg:" in line:
            avg = float(line.split(":")[1].strip())
        elif "P90:" in line:
            p90 = float(line.split(":")[1].strip())
        elif "P99:" in line:
            p99 = float(line.split(":")[1].strip())
            # All metrics collected for this benchmark
            results.append(
                {
                    "name": current_benchmark,
                    "ops_per_sec": ops_per_sec,
                    "avg": avg,
                    "p90": p90,
                    "p99": p99,
                }
            )
            current_benchmark = None

    return results


def generate_markdown_report(
    results: dict[str, list[dict]],
    concurrency: int,
    duration: int,
    output_file: str,
) -> None:
    """Generate a comprehensive markdown comparison report."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_file, "w") as f:
        f.write("# ScyllaDB/Cassandra Python Driver Benchmark Comparison\n\n")
        f.write(f"**Generated:** {timestamp}\n\n")
        f.write("**Test Configuration:**\n")
        f.write(f"- Concurrency: {concurrency}\n")
        f.write(f"- Duration: {duration} seconds per benchmark\n")
        f.write("- Key range: 0-65535 (random access)\n\n")

        f.write("## Executive Summary\n\n")
        f.write(
            "This report compares the performance of three Python drivers for ScyllaDB/Cassandra:\n\n"
        )
        f.write(
            "- **rsylla**: High-performance Python bindings built on the official Rust driver\n"
        )
        f.write("- **acsylla**: Asyncio-based Python wrapper around the C++ DataStax driver\n")
        f.write(
            "- **cassandra-driver**: Official DataStax Python driver (synchronous, thread-based)\n\n"
        )

        # Calculate overall winners
        f.write("### Quick Comparison\n\n")

        benchmark_types = set()
        for lib_results in results.values():
            for r in lib_results:
                benchmark_types.add(r["name"])

        for bench_type in sorted(benchmark_types):
            f.write(f"**{bench_type}:**\n\n")

            lib_ops = {}
            for lib, lib_results in results.items():
                for r in lib_results:
                    if r["name"] == bench_type:
                        lib_ops[lib] = r["ops_per_sec"]
                        break

            if lib_ops:
                winner = max(lib_ops, key=lib_ops.get)
                f.write("| Library | Ops/sec | Winner |\n")
                f.write("|---------|---------|--------|\n")
                for lib in ["rsylla", "acsylla", "cassandra-driver"]:
                    if lib in lib_ops:
                        is_winner = "🏆" if lib == winner else ""
                        f.write(f"| {lib} | {lib_ops[lib]:,} | {is_winner} |\n")
                f.write("\n")

        f.write("\n## Detailed Results\n\n")

        # Detailed comparison table for each benchmark type
        for bench_type in sorted(benchmark_types):
            f.write(f"### {bench_type}\n\n")
            f.write("| Library | Ops/sec | Avg Latency (s) | P90 Latency (s) | P99 Latency (s) |\n")
            f.write(
                "|---------|---------|-----------------|-----------------|------------------|\n"
            )

            for lib in ["rsylla", "acsylla", "cassandra-driver"]:
                if lib in results:
                    for r in results[lib]:
                        if r["name"] == bench_type:
                            f.write(
                                f"| {lib} | {r['ops_per_sec']:,} | {r['avg']:.6f} | "
                                f"{r['p90']:.6f} | {r['p99']:.6f} |\n"
                            )
                            break

            f.write("\n")

        # Performance comparison section
        f.write("## Performance Analysis\n\n")

        # Calculate speedup factors
        f.write("### Throughput Comparison\n\n")
        f.write("Relative performance (ops/sec) normalized to cassandra-driver baseline:\n\n")
        f.write("| Benchmark | rsylla | acsylla | cassandra-driver |\n")
        f.write("|-----------|--------|---------|------------------|\n")

        for bench_type in sorted(benchmark_types):
            baseline = None
            lib_values = {}

            for lib in ["rsylla", "acsylla", "cassandra-driver"]:
                if lib in results:
                    for r in results[lib]:
                        if r["name"] == bench_type:
                            lib_values[lib] = r["ops_per_sec"]
                            if lib == "cassandra-driver":
                                baseline = r["ops_per_sec"]
                            break

            if baseline and baseline > 0:
                row = f"| {bench_type} |"
                for lib in ["rsylla", "acsylla", "cassandra-driver"]:
                    if lib in lib_values:
                        speedup = lib_values[lib] / baseline
                        row += f" {speedup:.2f}x |"
                    else:
                        row += " N/A |"
                f.write(row + "\n")

        f.write("\n")

        # Latency comparison
        f.write("### Latency Comparison\n\n")
        f.write("Average latency comparison (lower is better):\n\n")
        f.write("| Benchmark | rsylla (ms) | acsylla (ms) | cassandra-driver (ms) |\n")
        f.write("|-----------|-------------|--------------|------------------------|\n")

        for bench_type in sorted(benchmark_types):
            row = f"| {bench_type} |"
            for lib in ["rsylla", "acsylla", "cassandra-driver"]:
                if lib in results:
                    for r in results[lib]:
                        if r["name"] == bench_type:
                            row += f" {r['avg'] * 1000:.3f} |"
                            break
                else:
                    row += " N/A |"
            f.write(row + "\n")

        f.write("\n")

        # Key findings
        f.write("## Key Findings\n\n")

        # Calculate average speedup for rsylla vs others
        rsylla_speedups = []
        acsylla_speedups = []

        for bench_type in sorted(benchmark_types):
            cassandra_ops = None
            rsylla_ops = None
            acsylla_ops = None

            for lib, lib_results in results.items():
                for r in lib_results:
                    if r["name"] == bench_type:
                        if lib == "cassandra-driver":
                            cassandra_ops = r["ops_per_sec"]
                        elif lib == "rsylla":
                            rsylla_ops = r["ops_per_sec"]
                        elif lib == "acsylla":
                            acsylla_ops = r["ops_per_sec"]

            if cassandra_ops and rsylla_ops:
                rsylla_speedups.append(rsylla_ops / cassandra_ops)
            if cassandra_ops and acsylla_ops:
                acsylla_speedups.append(acsylla_ops / cassandra_ops)

        if rsylla_speedups:
            avg_rsylla_speedup = sum(rsylla_speedups) / len(rsylla_speedups)
            f.write(
                f"- **rsylla** is on average **{avg_rsylla_speedup:.2f}x faster** than cassandra-driver\n"
            )

        if acsylla_speedups:
            avg_acsylla_speedup = sum(acsylla_speedups) / len(acsylla_speedups)
            f.write(
                f"- **acsylla** is on average **{avg_acsylla_speedup:.2f}x faster** than cassandra-driver\n"
            )

        if rsylla_speedups and acsylla_speedups:
            rsylla_vs_acsylla = []
            for bench_type in sorted(benchmark_types):
                rsylla_ops = None
                acsylla_ops = None

                for lib, lib_results in results.items():
                    for r in lib_results:
                        if r["name"] == bench_type:
                            if lib == "rsylla":
                                rsylla_ops = r["ops_per_sec"]
                            elif lib == "acsylla":
                                acsylla_ops = r["ops_per_sec"]

                if rsylla_ops and acsylla_ops:
                    rsylla_vs_acsylla.append(rsylla_ops / acsylla_ops)

            if rsylla_vs_acsylla:
                avg_ratio = sum(rsylla_vs_acsylla) / len(rsylla_vs_acsylla)
                if avg_ratio > 1:
                    f.write(
                        f"- **rsylla** is on average **{avg_ratio:.2f}x faster** than acsylla\n"
                    )
                else:
                    f.write(
                        f"- **acsylla** is on average **{1/avg_ratio:.2f}x faster** than rsylla\n"
                    )

        f.write("\n")

        # Recommendations
        f.write("## Recommendations\n\n")
        f.write("### When to use rsylla:\n")
        f.write("- Maximum throughput is required\n")
        f.write("- Modern async/await Python code\n")
        f.write("- Building on official ScyllaDB Rust driver\n")
        f.write("- Full type safety and IDE support needed\n\n")

        f.write("### When to use acsylla:\n")
        f.write("- Async/await support required\n")
        f.write("- Good balance of performance and maturity\n")
        f.write("- Existing acsylla codebase\n\n")

        f.write("### When to use cassandra-driver:\n")
        f.write("- Maximum compatibility with existing code\n")
        f.write("- Synchronous/thread-based architecture preferred\n")
        f.write("- Official DataStax support required\n")
        f.write("- Mature ecosystem and extensive documentation\n\n")

        # Raw data
        f.write("## Raw Benchmark Data\n\n")
        f.write("```json\n")
        f.write(json.dumps(results, indent=2))
        f.write("\n```\n")

    print(f"\n\nReport generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Run benchmarks for rsylla, acsylla, and cassandra-driver"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=32,
        help="Number of concurrent clients (default: 32)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="Duration of each benchmark in seconds (default: 10)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="ScyllaDB/Cassandra host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--keyspace",
        type=str,
        default="acsylla",
        help="Keyspace name (default: acsylla)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmark_results.md",
        help="Output markdown file (default: benchmark_results.md)",
    )
    parser.add_argument(
        "--libraries",
        nargs="+",
        choices=["rsylla", "acsylla", "cassandra-driver"],
        default=["rsylla", "acsylla", "cassandra-driver"],
        help="Libraries to benchmark (default: all)",
    )

    args = parser.parse_args()

    results = {}

    # Map library names to benchmark scripts
    scripts = {
        "rsylla": "benchmark/rsylla_benchmark.py",
        "acsylla": "/tmp/acsylla_benchmark.py",
        "cassandra-driver": "/tmp/cassandra_python_benchmark.py",
    }

    for lib in args.libraries:
        if lib not in scripts:
            print(f"Warning: Unknown library {lib}, skipping")
            continue

        script = scripts[lib]
        lib_results = run_benchmark(
            script, args.concurrency, args.duration, args.host, args.keyspace
        )

        if lib_results:
            results[lib] = lib_results
        else:
            print(f"Warning: No results for {lib}")

    if not results:
        print("Error: No benchmark results collected")
        sys.exit(1)

    generate_markdown_report(results, args.concurrency, args.duration, args.output)


if __name__ == "__main__":
    main()
