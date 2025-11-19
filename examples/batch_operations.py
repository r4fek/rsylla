"""
Example demonstrating batch operations with rsylla
"""

from rsylla import Batch, ScyllaError, Session


def main():
    print("Connecting to ScyllaDB...")
    session = Session.connect(["127.0.0.1:9042"])

    try:
        # Setup
        session.execute(
            """
            CREATE KEYSPACE IF NOT EXISTS example
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
            """
        )
        session.use_keyspace("example", case_sensitive=False)

        session.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id int,
                user_id int,
                product_id int,
                quantity int,
                PRIMARY KEY (order_id, user_id)
            )
            """
        )

        session.execute(
            """
            CREATE TABLE IF NOT EXISTS user_orders (
                user_id int,
                order_id int,
                total_items int,
                PRIMARY KEY (user_id, order_id)
            )
            """
        )

        session.await_schema_agreement()

        # Create a logged batch
        print("\nCreating logged batch...")
        batch = Batch("logged")

        # Add statements to batch
        batch.append_statement(
            "INSERT INTO orders (order_id, user_id, product_id, quantity) VALUES (?, ?, ?, ?)"
        )
        batch.append_statement(
            "INSERT INTO user_orders (user_id, order_id, total_items) VALUES (?, ?, ?)"
        )

        # Configure batch
        batch = batch.with_consistency("QUORUM").set_idempotent(False)

        # Execute batch with multiple sets of values
        print("Executing batch operations...")
        session.batch(
            batch,
            [
                {"order_id": 1, "user_id": 100, "product_id": 1, "quantity": 2},
                {"user_id": 100, "order_id": 1, "total_items": 2},
            ],
        )
        print("  Order 1 created")

        # Create another batch for different order
        batch2 = Batch("logged")
        batch2.append_statement(
            "INSERT INTO orders (order_id, user_id, product_id, quantity) VALUES (?, ?, ?, ?)"
        )
        batch2.append_statement(
            "INSERT INTO orders (order_id, user_id, product_id, quantity) VALUES (?, ?, ?, ?)"
        )
        batch2.append_statement(
            "INSERT INTO user_orders (user_id, order_id, total_items) VALUES (?, ?, ?)"
        )

        session.batch(
            batch2,
            [
                {"order_id": 2, "user_id": 100, "product_id": 1, "quantity": 1},
                {"order_id": 2, "user_id": 100, "product_id": 2, "quantity": 3},
                {"user_id": 100, "order_id": 2, "total_items": 4},
            ],
        )
        print("  Order 2 created")

        # Unlogged batch for better performance (no atomicity)
        print("\nCreating unlogged batch...")
        unlogged_batch = Batch("unlogged")
        unlogged_batch.append_statement(
            "INSERT INTO orders (order_id, user_id, product_id, quantity) VALUES (?, ?, ?, ?)"
        )
        unlogged_batch.append_statement(
            "INSERT INTO user_orders (user_id, order_id, total_items) VALUES (?, ?, ?)"
        )

        session.batch(
            unlogged_batch,
            [
                {"order_id": 3, "user_id": 101, "product_id": 3, "quantity": 5},
                {"user_id": 101, "order_id": 3, "total_items": 5},
            ],
        )
        print("  Order 3 created (unlogged)")

        # Query results
        print("\nQuerying orders...")
        result = session.execute("SELECT * FROM orders")
        for row in result:
            cols = row.columns()
            print(f"  Order {cols[0]}: User {cols[1]}, Product {cols[2]}, Qty {cols[3]}")

        print("\nQuerying user orders...")
        result = session.execute("SELECT * FROM user_orders")
        for row in result:
            cols = row.columns()
            print(f"  User {cols[0]}: Order {cols[1]}, Total items {cols[2]}")

        print(f"\nBatch has {batch.statements_count()} statements")
        print("\nExample completed successfully!")

    except ScyllaError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
