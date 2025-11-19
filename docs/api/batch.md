# Batch API Reference

## Batch

### Overview

`Batch` allows executing multiple statements atomically (for logged batches) or as a single request (for unlogged batches).

### Constructor

```python
batch = Batch(batch_type="logged")
```

**Parameters:**
- `batch_type`: Type of batch - `"logged"`, `"unlogged"`, or `"counter"`

**Batch Types:**

- **`"logged"`** (default): Atomicity guaranteed. All statements succeed or all fail. Higher latency.
- **`"unlogged"`**: No atomicity guarantee. Better performance. Use when statements are independent.
- **`"counter"`**: For counter updates only. All statements must be counter updates.

**Examples:**
```python
from rsylla import Batch

# Logged batch (default) - atomic
logged = Batch("logged")

# Unlogged batch - better performance
unlogged = Batch("unlogged")

# Counter batch - for counters only
counter_batch = Batch("counter")
```

### Methods

#### `append_statement(query: str) -> None`

Adds a query string to the batch.

**Parameters:**
- `query`: CQL query string with placeholders

**Example:**
```python
batch = Batch("logged")
batch.append_statement("INSERT INTO users (id, name) VALUES (?, ?)")
batch.append_statement("INSERT INTO user_index (name, id) VALUES (?, ?)")
```

#### `append_query(query: Query) -> None`

Adds a Query object to the batch.

**Parameters:**
- `query`: Query object

**Example:**
```python
from rsylla import Query

batch = Batch("unlogged")

query1 = Query("INSERT INTO logs (id, message) VALUES (?, ?)")
query2 = Query("UPDATE stats SET count = count + 1 WHERE id = ?")

batch.append_query(query1)
batch.append_query(query2)
```

#### `append_prepared(prepared: PreparedStatement) -> None`

Adds a PreparedStatement to the batch.

**Parameters:**
- `prepared`: PreparedStatement object

**Example:**
```python
batch = Batch("logged")

insert_user = session.prepare("INSERT INTO users (id, name) VALUES (?, ?)")
insert_email = session.prepare("INSERT INTO emails (user_id, email) VALUES (?, ?)")

batch.append_prepared(insert_user)
batch.append_prepared(insert_email)
```

#### `with_consistency(consistency: str) -> Batch`

Sets the consistency level for the batch.

**Parameters:**
- `consistency`: Consistency level name

**Returns:** Self for method chaining

**Example:**
```python
batch = Batch("logged").with_consistency("QUORUM")
```

#### `with_serial_consistency(serial_consistency: str) -> Batch`

Sets the serial consistency for lightweight transactions.

**Parameters:**
- `serial_consistency`: Serial consistency level

**Returns:** Self for method chaining

**Example:**
```python
batch = Batch("logged").with_serial_consistency("LOCAL_SERIAL")
```

#### `with_timestamp(timestamp: int) -> Batch`

Sets the timestamp for all statements in the batch.

**Parameters:**
- `timestamp`: Timestamp in microseconds

**Returns:** Self for method chaining

**Example:**
```python
import time

timestamp = int(time.time() * 1000000)
batch = Batch("logged").with_timestamp(timestamp)
```

#### `with_timeout(timeout_ms: int) -> Batch`

Sets the request timeout.

**Parameters:**
- `timeout_ms`: Timeout in milliseconds

**Returns:** Self for method chaining

**Example:**
```python
batch = Batch("logged").with_timeout(10000)  # 10 seconds
```

#### `with_tracing(tracing: bool) -> Batch`

Enables or disables tracing.

**Parameters:**
- `tracing`: True to enable tracing

**Returns:** Self for method chaining

**Example:**
```python
batch = Batch("logged").with_tracing(True)
```

#### `is_idempotent() -> bool`

Checks if the batch is idempotent.

**Returns:** True if idempotent

#### `set_idempotent(idempotent: bool) -> None`

Sets whether the batch is idempotent.

**Parameters:**
- `idempotent`: True if idempotent

**Example:**
```python
batch = Batch("unlogged")
batch.set_idempotent(True)
```

#### `statements_count() -> int`

Returns the number of statements in the batch.

**Returns:** Number of statements

**Example:**
```python
batch = Batch("logged")
batch.append_statement("INSERT INTO users (id, name) VALUES (?, ?)")
batch.append_statement("INSERT INTO users (id, name) VALUES (?, ?)")

print(f"Batch has {batch.statements_count()} statements")  # 2
```

### Executing Batches

Batches are executed using `Session.batch()`:

```python
result = session.batch(batch, values)
```

**Parameters:**
- `batch`: Batch object
- `values`: List of value dictionaries, one per statement

**Example:**
```python
batch = Batch("logged")
batch.append_statement("INSERT INTO users (id, name) VALUES (?, ?)")
batch.append_statement("INSERT INTO users (id, name) VALUES (?, ?)")

session.batch(batch, [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
])
```

### Complete Examples

#### Logged Batch - Atomic Writes

```python
from rsylla import Session, Batch

session = Session.connect(["127.0.0.1:9042"])
session.use_keyspace("myapp", False)

# Create logged batch for atomicity
batch = Batch("logged")

# Add statements that must all succeed or all fail
batch.append_statement("INSERT INTO users (id, name, email) VALUES (?, ?, ?)")
batch.append_statement("INSERT INTO user_by_email (email, user_id) VALUES (?, ?)")
batch.append_statement("UPDATE user_count SET count = count + 1 WHERE type = ?")

# Configure batch
batch = batch.with_consistency("QUORUM")

# Execute with values for each statement
session.batch(batch, [
    {"id": 123, "name": "Alice", "email": "alice@example.com"},
    {"email": "alice@example.com", "user_id": 123},
    {"type": "active"}
])

print("User created atomically")
```

#### Unlogged Batch - Performance

```python
# Use unlogged batch for better performance when atomicity isn't needed
batch = Batch("unlogged")

# Add independent inserts
batch.append_statement("INSERT INTO logs (id, timestamp, message) VALUES (?, ?, ?)")
batch.append_statement("INSERT INTO logs (id, timestamp, message) VALUES (?, ?, ?)")
batch.append_statement("INSERT INTO logs (id, timestamp, message) VALUES (?, ?, ?)")

# Configure for performance
batch = (
    batch
    .with_consistency("ONE")
    .set_idempotent(True)
)

# Execute batch
import time
timestamp = int(time.time() * 1000)

session.batch(batch, [
    {"id": 1, "timestamp": timestamp, "message": "Log message 1"},
    {"id": 2, "timestamp": timestamp + 1, "message": "Log message 2"},
    {"id": 3, "timestamp": timestamp + 2, "message": "Log message 3"}
])
```

#### Counter Batch

```python
# Counter batch for updating counters
counter_batch = Batch("counter")

counter_batch.append_statement("UPDATE page_views SET views = views + ? WHERE page_id = ?")
counter_batch.append_statement("UPDATE user_stats SET posts = posts + ? WHERE user_id = ?")

counter_batch = counter_batch.with_consistency("ONE")

session.batch(counter_batch, [
    {"views": 1, "page_id": "home"},
    {"posts": 1, "user_id": 456}
])
```

#### Batch with Prepared Statements

```python
# Prepare statements
insert_order = session.prepare(
    "INSERT INTO orders (order_id, user_id, total) VALUES (?, ?, ?)"
)

insert_order_items = session.prepare(
    "INSERT INTO order_items (order_id, item_id, quantity) VALUES (?, ?, ?)"
)

# Create batch
batch = Batch("logged")
batch.append_prepared(insert_order)
batch.append_prepared(insert_order_items)
batch.append_prepared(insert_order_items)

# Execute
session.batch(batch, [
    {"order_id": 1001, "user_id": 123, "total": 150.00},
    {"order_id": 1001, "item_id": 1, "quantity": 2},
    {"order_id": 1001, "item_id": 2, "quantity": 1}
])
```

#### Batch Updates with Same Partition Key

```python
# Best practice: batch statements for same partition key
user_id = 123

batch = Batch("logged")

# All statements operate on same partition
batch.append_statement("UPDATE users SET name = ? WHERE id = ?")
batch.append_statement("UPDATE users SET email = ? WHERE id = ?")
batch.append_statement("UPDATE users SET updated_at = ? WHERE id = ?")

import time
updated_at = int(time.time() * 1000)

batch = batch.with_timestamp(int(time.time() * 1000000))

session.batch(batch, [
    {"name": "Alice Updated", "id": user_id},
    {"email": "alice.new@example.com", "id": user_id},
    {"updated_at": updated_at, "id": user_id}
])
```

#### Mixed Batch (Queries and Prepared)

```python
# Prepare some statements
prepared_insert = session.prepare("INSERT INTO events (id, data) VALUES (?, ?)")

# Create batch with mixed statement types
batch = Batch("unlogged")

# Add prepared statement
batch.append_prepared(prepared_insert)

# Add query string
batch.append_statement("UPDATE stats SET count = count + 1 WHERE type = ?")

# Execute
session.batch(batch, [
    {"id": 1, "data": "event data"},
    {"type": "events"}
])
```

### Best Practices

#### 1. Use Logged Batches for Atomicity

```python
# When you need all-or-nothing semantics
batch = Batch("logged")  # Atomic
batch.append_statement("INSERT INTO accounts (id, balance) VALUES (?, ?)")
batch.append_statement("INSERT INTO transactions (id, amount) VALUES (?, ?)")
```

#### 2. Use Unlogged for Performance

```python
# When statements are independent
batch = Batch("unlogged")  # Faster
batch.append_statement("INSERT INTO logs (id, message) VALUES (?, ?)")
batch.append_statement("INSERT INTO logs (id, message) VALUES (?, ?)")
```

#### 3. Keep Batches Small

```python
# Don't batch too many statements
MAX_BATCH_SIZE = 100

statements = [...] # Many statements

for i in range(0, len(statements), MAX_BATCH_SIZE):
    batch = Batch("unlogged")
    batch_statements = statements[i:i+MAX_BATCH_SIZE]

    for stmt in batch_statements:
        batch.append_statement(stmt)

    # Execute batch
    session.batch(batch, batch_values[i:i+MAX_BATCH_SIZE])
```

#### 4. Batch Same Partition Key

```python
# Best performance: same partition key
user_id = 123

batch = Batch("logged")
batch.append_statement("INSERT INTO user_posts (user_id, post_id, title) VALUES (?, ?, ?)")
batch.append_statement("INSERT INTO user_posts (user_id, post_id, title) VALUES (?, ?, ?)")

session.batch(batch, [
    {"user_id": user_id, "post_id": 1, "title": "Post 1"},
    {"user_id": user_id, "post_id": 2, "title": "Post 2"}
])
```

### Anti-Patterns to Avoid

```python
# ❌ DON'T: Batch statements across many partitions
batch = Batch("unlogged")
for user_id in range(1000):  # Many different partitions
    batch.append_statement("UPDATE users SET login_count = login_count + 1 WHERE id = ?")
# This defeats the purpose of batching

# ✅ DO: Use prepared statements instead
prepared = session.prepare("UPDATE users SET login_count = login_count + 1 WHERE id = ?")
for user_id in range(1000):
    session.execute_prepared(prepared, {"id": user_id})

# ❌ DON'T: Use logged batches for unrelated writes
batch = Batch("logged")  # Unnecessary overhead
batch.append_statement("INSERT INTO logs (id, message) VALUES (?, ?)")
batch.append_statement("INSERT INTO metrics (id, value) VALUES (?, ?)")

# ✅ DO: Use unlogged or execute separately
batch = Batch("unlogged")  # Or just execute separately
```
