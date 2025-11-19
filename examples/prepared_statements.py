"""
Example demonstrating prepared statements with rscylla
"""

from rscylla import Session, ScyllaError


def main():
    print("Connecting to ScyllaDB...")
    session = Session.connect(["127.0.0.1:9042"])

    try:
        # Setup keyspace and table
        session.execute(
            """
            CREATE KEYSPACE IF NOT EXISTS example
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
            """
        )
        session.use_keyspace("example", case_sensitive=False)

        session.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id int PRIMARY KEY,
                name text,
                price double,
                quantity int
            )
            """
        )

        session.await_schema_agreement()

        # Prepare statements
        print("\nPreparing statements...")
        insert_prepared = session.prepare(
            "INSERT INTO products (id, name, price, quantity) VALUES (?, ?, ?, ?)"
        )

        select_prepared = session.prepare(
            "SELECT * FROM products WHERE id = ?"
        )

        update_prepared = session.prepare(
            "UPDATE products SET quantity = quantity + ? WHERE id = ?"
        )

        # Configure prepared statement
        insert_prepared = (
            insert_prepared
            .with_consistency("QUORUM")
            .set_idempotent(True)
        )

        # Insert data using prepared statement
        print("\nInserting products using prepared statements...")
        products = [
            {"id": 1, "name": "Laptop", "price": 999.99, "quantity": 10},
            {"id": 2, "name": "Mouse", "price": 29.99, "quantity": 50},
            {"id": 3, "name": "Keyboard", "price": 79.99, "quantity": 30},
        ]

        for product in products:
            session.execute_prepared(insert_prepared, product)
            print(f"  Inserted: {product['name']}")

        # Query using prepared statement
        print("\nQuerying products...")
        for product_id in [1, 2, 3]:
            result = session.execute_prepared(select_prepared, {"id": product_id})
            row = result.first_row()
            if row:
                cols = row.columns()
                print(f"  Product {cols[0]}: {cols[1]} - ${cols[2]:.2f} (qty: {cols[3]})")

        # Update using prepared statement
        print("\nUpdating inventory...")
        session.execute_prepared(update_prepared, {"quantity": 5, "id": 1})
        session.execute_prepared(update_prepared, {"quantity": -3, "id": 2})

        # Verify updates
        print("\nUpdated inventory:")
        result = session.execute("SELECT * FROM products")
        for row in result:
            cols = row.columns()
            print(f"  {cols[1]}: {cols[3]} units")

        # Get prepared statement info
        print(f"\nPrepared statement ID: {insert_prepared.get_id().hex()}")
        print(f"Statement: {insert_prepared.get_statement()}")

        print("\nExample completed successfully!")

    except ScyllaError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
