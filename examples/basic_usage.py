"""
Basic usage example for rscylla
"""

from rscylla import ScyllaError, Session


def main():
    # Connect to ScyllaDB cluster
    print("Connecting to ScyllaDB...")
    session = Session.connect(["127.0.0.1:9042"])

    try:
        # Create a keyspace
        print("Creating keyspace...")
        session.execute(
            """
            CREATE KEYSPACE IF NOT EXISTS example
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
            """
        )

        # Use the keyspace
        session.use_keyspace("example", case_sensitive=False)

        # Create a table
        print("Creating table...")
        session.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id int PRIMARY KEY,
                name text,
                email text,
                age int
            )
            """
        )

        # Wait for schema agreement
        if session.await_schema_agreement():
            print("Schema agreement reached")

        # Insert data
        print("Inserting data...")
        session.execute(
            "INSERT INTO users (id, name, email, age) VALUES (?, ?, ?, ?)",
            {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30},
        )

        session.execute(
            "INSERT INTO users (id, name, email, age) VALUES (?, ?, ?, ?)",
            {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 25},
        )

        session.execute(
            "INSERT INTO users (id, name, email, age) VALUES (?, ?, ?, ?)",
            {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 35},
        )

        # Query data
        print("\nQuerying all users...")
        result = session.execute("SELECT * FROM users")

        print(f"Found {len(result)} users:")
        for row in result:
            columns = row.columns()
            print(f"  ID: {columns[0]}, Name: {columns[1]}, Email: {columns[2]}, Age: {columns[3]}")

        # Query single user
        print("\nQuerying single user...")
        result = session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
        row = result.first_row()
        if row:
            columns = row.columns()
            print(f"User: {columns[1]} ({columns[2]}), Age: {columns[3]}")

        # Update data
        print("\nUpdating user...")
        session.execute("UPDATE users SET age = ? WHERE id = ?", {"age": 31, "id": 1})

        # Verify update
        result = session.execute("SELECT age FROM users WHERE id = ?", {"id": 1})
        row = result.single_row()
        print(f"Updated age: {row[0]}")

        # Delete data
        print("\nDeleting user...")
        session.execute("DELETE FROM users WHERE id = ?", {"id": 3})

        # Verify deletion
        result = session.execute("SELECT * FROM users")
        print(f"Users after deletion: {len(result)}")

        print("\nExample completed successfully!")

    except ScyllaError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
