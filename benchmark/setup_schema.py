#!/usr/bin/env python3
"""
Setup script for benchmark database schema.

Creates the keyspace and table needed for running benchmarks.
"""

import argparse
import asyncio

from rsylla import Session


async def setup_schema(host: str, keyspace: str, replication_factor: int = 1):
    """Create keyspace and table for benchmarks."""
    print(f"Connecting to {host}...")
    session = await Session.connect([host + ":9042"])

    print(f"Creating keyspace '{keyspace}' with replication factor {replication_factor}...")
    try:
        await session.execute(
            f"""
            CREATE KEYSPACE IF NOT EXISTS {keyspace}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': {replication_factor}}}
            """
        )
        print(f"Keyspace '{keyspace}' created successfully")
    except Exception as e:
        print(f"Error creating keyspace (may already exist): {e}")

    print(f"Using keyspace '{keyspace}'...")
    await session.use_keyspace(keyspace, case_sensitive=False)

    print("Creating table 'test'...")
    try:
        await session.execute(
            """
            CREATE TABLE IF NOT EXISTS test (
                id int PRIMARY KEY,
                value int
            )
            """
        )
        print("Table 'test' created successfully")
    except Exception as e:
        print(f"Error creating table (may already exist): {e}")

    # Insert some initial data to ensure the table is not empty
    print("Inserting initial test data...")
    try:
        for i in range(100):
            await session.execute(
                "INSERT INTO test (id, value) VALUES (?, ?)", {"id": i, "value": i}
            )
        print("Initial data inserted successfully")
    except Exception as e:
        print(f"Error inserting initial data: {e}")

    print("\nSchema setup complete!")
    print("\nYou can now run benchmarks with:")
    print(f"  python benchmark/run_all_benchmarks.py --host {host} --keyspace {keyspace}")


def main():
    parser = argparse.ArgumentParser(description="Setup database schema for benchmarks")
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
        "--replication-factor",
        type=int,
        default=1,
        help="Replication factor (default: 1)",
    )

    args = parser.parse_args()

    asyncio.run(setup_schema(args.host, args.keyspace, args.replication_factor))


if __name__ == "__main__":
    main()
