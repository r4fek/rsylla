"""
Example demonstrating advanced session configuration with rscylla
"""

from rscylla import SessionBuilder, Query, ScyllaError


def main():
    print("Creating session with advanced configuration...")

    # Build session with custom configuration
    session = (
        SessionBuilder()
        .known_nodes(["127.0.0.1:9042"])
        .connection_timeout(10000)  # 10 seconds
        .pool_size(20)  # Connection pool size
        .compression("lz4")  # Enable LZ4 compression
        .tcp_nodelay(True)  # Disable Nagle's algorithm
        .tcp_keepalive(60000)  # 60 seconds keepalive
        .build()
    )

    print("Session created successfully!")
    print(f"Current keyspace: {session.get_keyspace()}")

    try:
        # Create keyspace with different replication
        print("\nCreating keyspace with NetworkTopologyStrategy...")
        session.execute(
            """
            CREATE KEYSPACE IF NOT EXISTS example_advanced
            WITH replication = {
                'class': 'NetworkTopologyStrategy',
                'datacenter1': 3
            }
            """
        )

        session.use_keyspace("example_advanced", case_sensitive=False)

        # Create table
        session.execute(
            """
            CREATE TABLE IF NOT EXISTS sensors (
                sensor_id int,
                timestamp bigint,
                temperature double,
                humidity double,
                PRIMARY KEY (sensor_id, timestamp)
            ) WITH CLUSTERING ORDER BY (timestamp DESC)
            """
        )

        session.await_schema_agreement()

        # Create query with advanced options
        print("\nExecuting query with advanced options...")
        query = (
            Query("INSERT INTO sensors (sensor_id, timestamp, temperature, humidity) VALUES (?, ?, ?, ?)")
            .with_consistency("LOCAL_QUORUM")
            .with_serial_consistency("LOCAL_SERIAL")
            .with_timestamp(1234567890000)
            .with_timeout(5000)
            .with_tracing(True)
            .set_idempotent(True)
        )

        query.set_idempotent(True)
        print(f"Query is idempotent: {query.is_idempotent()}")

        # Execute query
        result = session.query(
            query,
            {
                "sensor_id": 1,
                "timestamp": 1234567890000,
                "temperature": 22.5,
                "humidity": 45.0
            }
        )

        # Check tracing
        if result.tracing_id():
            print(f"Tracing ID: {result.tracing_id()}")

        # Insert more data
        for i in range(5):
            session.execute(
                "INSERT INTO sensors (sensor_id, timestamp, temperature, humidity) VALUES (?, ?, ?, ?)",
                {
                    "sensor_id": 1,
                    "timestamp": 1234567890000 + i * 1000,
                    "temperature": 20.0 + i * 0.5,
                    "humidity": 40.0 + i * 2.0
                }
            )

        # Query with paging
        print("\nQuerying with paging...")
        paged_query = Query("SELECT * FROM sensors WHERE sensor_id = ?").with_page_size(2)

        result = session.query(paged_query, {"sensor_id": 1})
        print(f"Retrieved {len(result)} readings")

        # Get column specifications
        print("\nColumn specifications:")
        col_specs = result.col_specs()
        for spec in col_specs:
            print(f"  {spec}")

        # Check for warnings
        warnings = result.warnings()
        if warnings:
            print(f"\nWarnings: {warnings}")
        else:
            print("\nNo warnings")

        # Get cluster data
        print(f"\nCluster data: {session.get_cluster_data()}")

        print("\nExample completed successfully!")

    except ScyllaError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
