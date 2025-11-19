# Getting Started with rsylla

This tutorial will walk you through the basics of using rsylla to interact with ScyllaDB.

## Prerequisites

- Python 3.8 or higher
- ScyllaDB or Cassandra running (locally or remote)
- rsylla installed (`pip install rsylla`)

## Starting ScyllaDB

If you don't have ScyllaDB running, the easiest way is using Docker:

```bash
docker run --name scylla -d -p 9042:9042 scylladb/scylla
```

Wait about 30 seconds for ScyllaDB to start, then verify:

```bash
docker logs scylla | grep "Scylla version"
```

## Step 1: Connecting to ScyllaDB

The simplest way to connect is using `Session.connect()`:

```python
from rsylla import Session

# Connect to local ScyllaDB
session = Session.connect(["127.0.0.1:9042"])

print("Connected to ScyllaDB!")
```

For production environments with multiple nodes and authentication:

```python
from rsylla import SessionBuilder

session = (
    SessionBuilder()
    .known_nodes([
        "node1.example.com:9042",
        "node2.example.com:9042",
        "node3.example.com:9042"
    ])
    .user("myuser", "mypassword")
    .compression("lz4")
    .connection_timeout(10000)
    .build()
)

print("Connected to production cluster!")
```

## Step 2: Creating a Keyspace

A keyspace is like a database in SQL. Create one:

```python
# Create keyspace
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS tutorial
    WITH replication = {
        'class': 'SimpleStrategy',
        'replication_factor': 1
    }
""")

# Use the keyspace
session.use_keyspace("tutorial", case_sensitive=False)

print("Keyspace created and selected!")
```

For production with multiple datacenters:

```python
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS production
    WITH replication = {
        'class': 'NetworkTopologyStrategy',
        'datacenter1': 3,
        'datacenter2': 3
    }
""")
```

## Step 3: Creating a Table

Create a simple users table:

```python
session.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id int PRIMARY KEY,
        username text,
        email text,
        created_at timestamp,
        is_active boolean
    )
""")

# Wait for schema to sync across cluster
if session.await_schema_agreement():
    print("Table created successfully!")
```

## Step 4: Inserting Data

Insert data using simple queries:

```python
# Insert a single user
session.execute("""
    INSERT INTO users (user_id, username, email, created_at, is_active)
    VALUES (?, ?, ?, ?, ?)
""", {
    "user_id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "created_at": 1234567890000,  # Timestamp in milliseconds
    "is_active": True
})

print("User inserted!")
```

Insert multiple users:

```python
users_data = [
    (2, "bob", "bob@example.com", 1234567891000, True),
    (3, "charlie", "charlie@example.com", 1234567892000, False),
    (4, "diana", "diana@example.com", 1234567893000, True),
]

for user_id, username, email, created_at, is_active in users_data:
    session.execute(
        "INSERT INTO users (user_id, username, email, created_at, is_active) VALUES (?, ?, ?, ?, ?)",
        {
            "user_id": user_id,
            "username": username,
            "email": email,
            "created_at": created_at,
            "is_active": is_active
        }
    )

print(f"Inserted {len(users_data)} users!")
```

## Step 5: Querying Data

Query all users:

```python
result = session.execute("SELECT * FROM users")

print(f"Found {len(result)} users:")
for row in result:
    user_id, username, email, created_at, is_active = row.columns()
    print(f"  {user_id}: {username} ({email}) - Active: {is_active}")
```

Query a specific user:

```python
result = session.execute(
    "SELECT * FROM users WHERE user_id = ?",
    {"user_id": 1}
)

row = result.first_row()
if row:
    user_id, username, email, created_at, is_active = row.columns()
    print(f"User: {username} ({email})")
else:
    print("User not found")
```

## Step 6: Updating Data

Update a user's information:

```python
session.execute(
    "UPDATE users SET email = ? WHERE user_id = ?",
    {"email": "alice.new@example.com", "user_id": 1}
)

print("User updated!")

# Verify the update
result = session.execute(
    "SELECT username, email FROM users WHERE user_id = ?",
    {"user_id": 1}
)
row = result.first_row()
if row:
    print(f"Updated user: {row[0]} - {row[1]}")
```

Update multiple fields:

```python
import time

session.execute("""
    UPDATE users
    SET username = ?, is_active = ?, created_at = ?
    WHERE user_id = ?
""", {
    "username": "alice_updated",
    "is_active": False,
    "created_at": int(time.time() * 1000),
    "user_id": 1
})
```

## Step 7: Deleting Data

Delete a specific user:

```python
session.execute(
    "DELETE FROM users WHERE user_id = ?",
    {"user_id": 4}
)

print("User deleted!")
```

Delete specific columns:

```python
# Delete only the email
session.execute(
    "DELETE email FROM users WHERE user_id = ?",
    {"user_id": 3}
)
```

## Step 8: Using Prepared Statements

For better performance with repeated queries, use prepared statements:

```python
# Prepare once
insert_stmt = session.prepare(
    "INSERT INTO users (user_id, username, email, created_at, is_active) VALUES (?, ?, ?, ?, ?)"
)

# Execute many times
import time
current_time = int(time.time() * 1000)

for i in range(100, 110):
    session.execute_prepared(insert_stmt, {
        "user_id": i,
        "username": f"user{i}",
        "email": f"user{i}@example.com",
        "created_at": current_time,
        "is_active": True
    })

print("Inserted 10 users using prepared statement!")
```

Benefits of prepared statements:
- Faster execution (query parsed once)
- More efficient network protocol
- Better for high-throughput scenarios

## Step 9: Working with Query Options

Use the Query class for advanced options:

```python
from rsylla import Query

# Query with consistency level
query = (
    Query("SELECT * FROM users WHERE user_id = ?")
    .with_consistency("QUORUM")
    .with_timeout(5000)
)

result = session.query(query, {"user_id": 1})
print(f"Found user: {result.first_row().columns()}")
```

Enable tracing to debug slow queries:

```python
query = (
    Query("SELECT * FROM users")
    .with_tracing(True)
)

result = session.query(query)

if result.tracing_id():
    print(f"Trace ID: {result.tracing_id()}")
    # You can query system_traces.sessions and system_traces.events
    # with this trace ID to see query execution details
```

## Step 10: Complete Example Application

Here's a complete example putting it all together:

```python
from rsylla import Session, Query
import time

def main():
    # Connect
    print("Connecting to ScyllaDB...")
    session = Session.connect(["127.0.0.1:9042"])

    # Create keyspace
    print("Setting up database...")
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS tutorial
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
    """)
    session.use_keyspace("tutorial", False)

    # Create table
    session.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id int PRIMARY KEY,
            username text,
            email text,
            created_at timestamp,
            is_active boolean
        )
    """)
    session.await_schema_agreement()

    # Prepare statements
    insert_stmt = session.prepare(
        "INSERT INTO users (user_id, username, email, created_at, is_active) VALUES (?, ?, ?, ?, ?)"
    )

    # Insert data
    print("Inserting users...")
    current_time = int(time.time() * 1000)

    users = [
        (1, "alice", "alice@example.com"),
        (2, "bob", "bob@example.com"),
        (3, "charlie", "charlie@example.com"),
    ]

    for user_id, username, email in users:
        session.execute_prepared(insert_stmt, {
            "user_id": user_id,
            "username": username,
            "email": email,
            "created_at": current_time,
            "is_active": True
        })

    # Query data
    print("\nQuerying users...")
    query = Query("SELECT * FROM users").with_consistency("ONE")
    result = session.query(query)

    print(f"Found {len(result)} users:")
    for row in result:
        cols = row.columns()
        print(f"  ID: {cols[0]}, Username: {cols[1]}, Email: {cols[2]}")

    # Update user
    print("\nUpdating user...")
    session.execute(
        "UPDATE users SET email = ? WHERE user_id = ?",
        {"email": "alice.updated@example.com", "user_id": 1}
    )

    # Verify update
    result = session.execute(
        "SELECT username, email FROM users WHERE user_id = ?",
        {"user_id": 1}
    )
    row = result.first_row()
    if row:
        print(f"Updated: {row[0]} - {row[1]}")

    # Delete user
    print("\nDeleting user...")
    session.execute("DELETE FROM users WHERE user_id = ?", {"user_id": 3})

    # Final count
    result = session.execute("SELECT COUNT(*) FROM users")
    count = result.first_row()[0]
    print(f"\nFinal user count: {count}")

    print("\nTutorial completed!")

if __name__ == "__main__":
    main()
```

## Next Steps

Now that you understand the basics, explore:

1. **[Batch Operations](batch-operations.md)** - Execute multiple statements atomically
2. **[Data Types](../guides/data-types.md)** - Working with CQL data types
3. **[Best Practices](../guides/best-practices.md)** - Performance and design patterns
4. **[Advanced Features](advanced-features.md)** - Consistency levels, paging, tracing

## Common Patterns

### Check if Row Exists

```python
result = session.execute(
    "SELECT user_id FROM users WHERE user_id = ?",
    {"user_id": 1}
)

if result.first_row():
    print("User exists")
else:
    print("User not found")
```

### Get or Create

```python
result = session.execute(
    "SELECT * FROM users WHERE user_id = ?",
    {"user_id": 1}
)

if not result.first_row():
    # User doesn't exist, create it
    session.execute(
        "INSERT INTO users (user_id, username, email) VALUES (?, ?, ?)",
        {"user_id": 1, "username": "alice", "email": "alice@example.com"}
    )
```

### Conditional Updates (LWT)

```python
# Only update if condition is met
result = session.execute(
    "UPDATE users SET email = ? WHERE user_id = ? IF is_active = ?",
    {"email": "new@example.com", "user_id": 1, "is_active": True}
)

# Check if update was applied
row = result.first_row()
if row and row[0]:  # [applied] column
    print("Update successful")
else:
    print("Condition not met")
```

## Troubleshooting

### Connection Refused

If you get connection errors:
```python
from rsylla import ScyllaError

try:
    session = Session.connect(["127.0.0.1:9042"])
except ScyllaError as e:
    print(f"Connection failed: {e}")
    print("Make sure ScyllaDB is running on port 9042")
```

### Keyspace Not Found

```python
try:
    session.use_keyspace("nonexistent", False)
except ScyllaError as e:
    print(f"Keyspace error: {e}")
```

### Query Errors

```python
try:
    result = session.execute("INVALID QUERY")
except ScyllaError as e:
    print(f"Query failed: {e}")
```
