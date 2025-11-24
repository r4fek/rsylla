import argparse
import asyncio
import random
import time

from rsylla import Session

MAX_NUMBER_OF_KEYS = 65536

prepared_statement_write = None
prepared_statement_read = None


async def write(session, key, value, str_key, str_value):
    start = time.monotonic()
    await session.execute("INSERT INTO test (id, value) values(" + str_key + "," + str_value + ")")
    return time.monotonic() - start


async def write_bind(session, key, value, *args):
    start = time.monotonic()
    await session.execute("INSERT INTO test (id, value) values(?, ?)", {"id": key, "value": value})
    return time.monotonic() - start


async def write_prepared(session, key, value, *args):
    start = time.monotonic()
    await session.execute_prepared(prepared_statement_write, {"id": key, "value": value})
    return time.monotonic() - start


async def read(session, key, value, str_key, str_value):
    start = time.monotonic()
    result = await session.execute("SELECT id, value FROM test WHERE id =" + str_key)
    if len(result) > 0:
        row = result.first_row()
        if row:
            _ = row.columns()
    return time.monotonic() - start


async def read_bind(session, key, value, *args):
    start = time.monotonic()
    result = await session.execute("SELECT id, value FROM test WHERE id = ?", {"id": key})
    if len(result) > 0:
        row = result.first_row()
        if row:
            _ = row.columns()
    return time.monotonic() - start


async def read_prepared(session, key, value, *args):
    start = time.monotonic()
    result = await session.execute_prepared(prepared_statement_read, {"id": key})
    if len(result) > 0:
        row = result.first_row()
        if row:
            _ = row.columns()
    return time.monotonic() - start


async def benchmark(desc: str, coro, session, concurrency: int, duration: int) -> dict:
    print(f"Starting benchmark {desc}")

    not_finish_benchmark = True

    async def run():
        nonlocal not_finish_benchmark
        times = []
        while not_finish_benchmark:
            key = random.randint(0, MAX_NUMBER_OF_KEYS)
            value = key
            str_key = str(key)
            str_value = str_key
            elapsed = await coro(session, key, value, str_key, str_value)
            times.append(elapsed)
        return times

    tasks = [asyncio.ensure_future(run()) for _ in range(concurrency)]

    await asyncio.sleep(duration)

    not_finish_benchmark = False
    while not all(task.done() for task in tasks):
        await asyncio.sleep(0)

    times = []
    for task in tasks:
        times += task.result()

    times.sort()

    total_ops = len(times)
    avg = sum(times) / total_ops if total_ops > 0 else 0

    p90 = times[int((90 * total_ops) / 100)] if total_ops > 0 else 0
    p99 = times[int((99 * total_ops) / 100)] if total_ops > 0 else 0

    print("Tests results:")
    print(f"\tOps/sec: {int(total_ops / duration)}")
    print(f"\tAvg: {avg:.6f}")
    print(f"\tP90: {p90:.6f}")
    print(f"\tP99: {p99:.6f}")

    return {
        "name": desc,
        "ops_per_sec": int(total_ops / duration),
        "avg": avg,
        "p90": p90,
        "p99": p99,
        "total_ops": total_ops,
    }


async def main():
    global prepared_statement_write, prepared_statement_read
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--concurrency",
        help="Number of concurrency clients, by default 32",
        type=int,
        default=32,
    )
    parser.add_argument(
        "--duration",
        help="Test duration in seconds, by default 60",
        type=int,
        default=60,
    )
    parser.add_argument(
        "--host",
        help="ScyllaDB/Cassandra host, by default 127.0.0.1",
        type=str,
        default="127.0.0.1",
    )
    parser.add_argument(
        "--keyspace",
        help="Keyspace name, by default acsylla",
        type=str,
        default="acsylla",
    )
    args = parser.parse_args()

    session = await Session.connect([args.host + ":9042"])
    await session.use_keyspace(args.keyspace, case_sensitive=False)

    prepared_statement_write = await session.prepare("INSERT INTO test (id, value) values(?, ?)")
    prepared_statement_read = await session.prepare("SELECT id, value FROM test WHERE id = ?")

    results = []

    results.append(await benchmark("write", write, session, args.concurrency, args.duration))
    results.append(
        await benchmark("write_bind", write_bind, session, args.concurrency, args.duration)
    )
    results.append(
        await benchmark("write_prepared", write_prepared, session, args.concurrency, args.duration)
    )
    results.append(await benchmark("read", read, session, args.concurrency, args.duration))
    results.append(
        await benchmark("read_bind", read_bind, session, args.concurrency, args.duration)
    )
    results.append(
        await benchmark("read_prepared", read_prepared, session, args.concurrency, args.duration)
    )

    return results


if __name__ == "__main__":
    results = asyncio.run(main())

    print("\n" + "=" * 80)
    print("SUMMARY - rsylla")
    print("=" * 80)
    for result in results:
        print(
            f"{result['name']:30s} | {result['ops_per_sec']:10d} ops/sec | "
            f"avg: {result['avg']:.6f}s | p90: {result['p90']:.6f}s | p99: {result['p99']:.6f}s"
        )
