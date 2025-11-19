# Data Types Guide

This guide explains how CQL data types are mapped to Python types in rsylla.

## Basic Types

### Integer Types

| CQL Type | Python Type | Range | Example |
|----------|-------------|-------|---------|
| `tinyint` | `int` | -128 to 127 | `42` |
| `smallint` | `int` | -32,768 to 32,767 | `1000` |
| `int` | `int` | -2³¹ to 2³¹-1 | `123456` |
| `bigint` | `int` | -2⁶³ to 2⁶³-1 | `9223372036854775807` |

**Example:**
```python
# Creating table with integer types
session.execute("""
    CREATE TABLE numbers (
        id int PRIMARY KEY,
        tiny tinyint,
        small smallint,
        big bigint
    )
""")

# Inserting
session.execute(
    "INSERT INTO numbers (id, tiny, small, big) VALUES (?, ?, ?, ?)",
    {"id": 1, "tiny": 42, "small": 1000, "big": 9223372036854775807}
)

# Querying
result = session.execute("SELECT * FROM numbers WHERE id = ?", {"id": 1})
row = result.first_row()
id, tiny, small, big = row.columns()
print(f"ID: {id} (int), Tiny: {tiny} (int), Small: {small} (int), Big: {big} (int)")
```

### Floating Point Types

| CQL Type | Python Type | Example |
|----------|-------------|---------|
| `float` | `float` | `3.14` |
| `double` | `float` | `3.141592653589793` |

**Example:**
```python
session.execute("""
    CREATE TABLE measurements (
        id int PRIMARY KEY,
        temperature float,
        precise_value double
    )
""")

session.execute(
    "INSERT INTO measurements (id, temperature, precise_value) VALUES (?, ?, ?)",
    {"id": 1, "temperature": 22.5, "precise_value": 3.141592653589793}
)
```

### Text Types

| CQL Type | Python Type | Description |
|----------|-------------|-------------|
| `text` | `str` | UTF-8 encoded string |
| `varchar` | `str` | Alias for text |
| `ascii` | `str` | ASCII string |

**Example:**
```python
session.execute("""
    CREATE TABLE messages (
        id int PRIMARY KEY,
        message text,
        author varchar,
        ascii_data ascii
    )
""")

session.execute(
    "INSERT INTO messages (id, message, author) VALUES (?, ?, ?)",
    {"id": 1, "message": "Hello, World! 你好", "author": "Alice"}
)

result = session.execute("SELECT * FROM messages WHERE id = ?", {"id": 1})
row = result.first_row()
print(f"Message: {row[1]} (type: {type(row[1])})")  # str
```

### Boolean

| CQL Type | Python Type | Values |
|----------|-------------|--------|
| `boolean` | `bool` | `True`, `False` |

**Example:**
```python
session.execute("""
    CREATE TABLE users (
        id int PRIMARY KEY,
        is_active boolean,
        email_verified boolean
    )
""")

session.execute(
    "INSERT INTO users (id, is_active, email_verified) VALUES (?, ?, ?)",
    {"id": 1, "is_active": True, "email_verified": False}
)
```

### Binary Data

| CQL Type | Python Type | Description |
|----------|-------------|-------------|
| `blob` | `bytes` | Raw binary data |

**Example:**
```python
session.execute("""
    CREATE TABLE files (
        id int PRIMARY KEY,
        data blob
    )
""")

# Insert binary data
binary_data = b'\x00\x01\x02\x03\x04\x05'
session.execute(
    "INSERT INTO files (id, data) VALUES (?, ?)",
    {"id": 1, "data": binary_data}
)

# Query binary data
result = session.execute("SELECT data FROM files WHERE id = ?", {"id": 1})
row = result.first_row()
data = row[0]
print(f"Data: {data} (type: {type(data)})")  # bytes
```

## Temporal Types

### Timestamp

| CQL Type | Python Type | Description |
|----------|-------------|-------------|
| `timestamp` | `int` | Milliseconds since epoch |

**Example:**
```python
import time

session.execute("""
    CREATE TABLE events (
        id int PRIMARY KEY,
        created_at timestamp,
        updated_at timestamp
    )
""")

# Current timestamp in milliseconds
current_time = int(time.time() * 1000)

session.execute(
    "INSERT INTO events (id, created_at, updated_at) VALUES (?, ?, ?)",
    {"id": 1, "created_at": current_time, "updated_at": current_time}
)

# Convert back to datetime
result = session.execute("SELECT created_at FROM events WHERE id = ?", {"id": 1})
timestamp_ms = result.first_row()[0]
from datetime import datetime
dt = datetime.fromtimestamp(timestamp_ms / 1000)
print(f"Created at: {dt}")
```

### Date and Time

| CQL Type | Python Type | Description |
|----------|-------------|-------------|
| `date` | `int` | Days since epoch (Jan 1, 1970) |
| `time` | `int` | Nanoseconds since midnight |

**Example:**
```python
session.execute("""
    CREATE TABLE schedules (
        id int PRIMARY KEY,
        event_date date,
        event_time time
    )
""")

# Date: days since epoch
from datetime import date
today = date.today()
days_since_epoch = (today - date(1970, 1, 1)).days

# Time: nanoseconds since midnight
from datetime import datetime
now = datetime.now()
nanoseconds = (now.hour * 3600 + now.minute * 60 + now.second) * 1_000_000_000

session.execute(
    "INSERT INTO schedules (id, event_date, event_time) VALUES (?, ?, ?)",
    {"id": 1, "event_date": days_since_epoch, "event_time": nanoseconds}
)
```

## UUID Types

| CQL Type | Python Type | Description |
|----------|-------------|-------------|
| `uuid` | `str` | UUID string |
| `timeuuid` | `str` | Time-based UUID |

**Example:**
```python
import uuid

session.execute("""
    CREATE TABLE items (
        id uuid PRIMARY KEY,
        timeuuid_col timeuuid,
        name text
    )
""")

# Generate UUIDs
item_id = str(uuid.uuid4())
time_uuid = str(uuid.uuid1())

session.execute(
    "INSERT INTO items (id, timeuuid_col, name) VALUES (?, ?, ?)",
    {"id": item_id, "timeuuid_col": time_uuid, "name": "Item 1"}
)

result = session.execute("SELECT * FROM items WHERE id = ?", {"id": item_id})
row = result.first_row()
print(f"ID: {row[0]} (str)")
print(f"TimeUUID: {row[1]} (str)")
```

## Collection Types

### List

| CQL Type | Python Type | Example |
|----------|-------------|---------|
| `list<type>` | `list` | `[1, 2, 3]` |

**Example:**
```python
session.execute("""
    CREATE TABLE users (
        id int PRIMARY KEY,
        tags list<text>,
        scores list<int>
    )
""")

session.execute(
    "INSERT INTO users (id, tags, scores) VALUES (?, ?, ?)",
    {"id": 1, "tags": ["admin", "moderator", "user"], "scores": [100, 95, 88]}
)

# Query
result = session.execute("SELECT tags, scores FROM users WHERE id = ?", {"id": 1})
row = result.first_row()
tags, scores = row.columns()
print(f"Tags: {tags} (type: {type(tags)})")  # list
print(f"Scores: {scores} (type: {type(scores)})")  # list

# Update list - append
session.execute(
    "UPDATE users SET tags = tags + ? WHERE id = ?",
    {"tags": ["premium"], "id": 1}
)

# Update list - prepend
session.execute(
    "UPDATE users SET tags = ? + tags WHERE id = ?",
    {"tags": ["new"], "id": 1}
)
```

### Set

| CQL Type | Python Type | Example |
|----------|-------------|---------|
| `set<type>` | `list` | `[1, 2, 3]` |

**Example:**
```python
session.execute("""
    CREATE TABLE products (
        id int PRIMARY KEY,
        categories set<text>,
        tags set<text>
    )
""")

# Sets automatically handle duplicates
session.execute(
    "INSERT INTO products (id, categories, tags) VALUES (?, ?, ?)",
    {"id": 1, "categories": ["electronics", "computers"], "tags": ["laptop", "portable"]}
)

# Add to set
session.execute(
    "UPDATE products SET categories = categories + ? WHERE id = ?",
    {"categories": ["gaming"], "id": 1}
)

# Remove from set
session.execute(
    "UPDATE products SET categories = categories - ? WHERE id = ?",
    {"categories": ["electronics"], "id": 1}
)
```

### Map

| CQL Type | Python Type | Example |
|----------|-------------|---------|
| `map<keytype, valuetype>` | `dict` | `{"key": "value"}` |

**Example:**
```python
session.execute("""
    CREATE TABLE users (
        id int PRIMARY KEY,
        attributes map<text, text>,
        scores map<text, int>
    )
""")

session.execute(
    "INSERT INTO users (id, attributes, scores) VALUES (?, ?, ?)",
    {
        "id": 1,
        "attributes": {"city": "New York", "country": "USA", "timezone": "EST"},
        "scores": {"math": 95, "science": 88, "english": 92}
    }
)

# Query
result = session.execute("SELECT attributes, scores FROM users WHERE id = ?", {"id": 1})
row = result.first_row()
attributes, scores = row.columns()
print(f"Attributes: {attributes} (type: {type(attributes)})")  # dict
print(f"City: {attributes.get('city')}")

# Update map - add/update entries
session.execute(
    "UPDATE users SET attributes = attributes + ? WHERE id = ?",
    {"attributes": {"language": "English"}, "id": 1}
)

# Delete map entry
session.execute(
    "DELETE attributes['timezone'] FROM users WHERE id = ?",
    {"id": 1}
)
```

## Advanced Types

### Counter

| CQL Type | Python Type | Description |
|----------|-------------|-------------|
| `counter` | `int` | Integer that can only be incremented/decremented |

**Example:**
```python
session.execute("""
    CREATE TABLE page_views (
        page_id text PRIMARY KEY,
        views counter
    )
""")

# Increment counter
session.execute(
    "UPDATE page_views SET views = views + ? WHERE page_id = ?",
    {"views": 1, "page_id": "homepage"}
)

# Decrement counter
session.execute(
    "UPDATE page_views SET views = views - ? WHERE page_id = ?",
    {"views": 1, "page_id": "homepage"}
)

# Query counter
result = session.execute("SELECT views FROM page_views WHERE page_id = ?", {"page_id": "homepage"})
views = result.first_row()[0]
print(f"Page views: {views}")
```

### Tuple

| CQL Type | Python Type | Example |
|----------|-------------|---------|
| `tuple<type1, type2, ...>` | `list` | `[1, "text", True]` |

**Example:**
```python
session.execute("""
    CREATE TABLE locations (
        id int PRIMARY KEY,
        coordinates tuple<double, double>,
        metadata tuple<text, int, boolean>
    )
""")

session.execute(
    "INSERT INTO locations (id, coordinates, metadata) VALUES (?, ?, ?)",
    {
        "id": 1,
        "coordinates": [40.7128, -74.0060],  # lat, lon
        "metadata": ["New York", 8000000, True]  # name, population, is_capital
    }
)

result = session.execute("SELECT coordinates FROM locations WHERE id = ?", {"id": 1})
coordinates = result.first_row()[0]
lat, lon = coordinates
print(f"Location: {lat}, {lon}")
```

### Duration

| CQL Type | Python Type | Description |
|----------|-------------|-------------|
| `duration` | `dict` | Time duration with months, days, nanoseconds |

**Example:**
```python
session.execute("""
    CREATE TABLE tasks (
        id int PRIMARY KEY,
        estimated_time duration
    )
""")

# Duration is represented as a dict with months, days, nanoseconds
# When querying, you'll receive a dict:
# {"months": 0, "days": 1, "nanoseconds": 3600000000000}

# Note: Inserting durations requires special handling
# In practice, you might want to use bigint for simpler duration tracking
```

### Decimal and Varint

| CQL Type | Python Type | Description |
|----------|-------------|-------------|
| `decimal` | `str` | Arbitrary-precision decimal |
| `varint` | `str` | Arbitrary-precision integer |

**Example:**
```python
session.execute("""
    CREATE TABLE financial (
        id int PRIMARY KEY,
        balance decimal,
        large_number varint
    )
""")

# These are returned as strings to preserve precision
result = session.execute("SELECT balance FROM financial WHERE id = ?", {"id": 1})
balance_str = result.first_row()[0]

# Convert to Decimal for calculations
from decimal import Decimal
balance = Decimal(balance_str)
```

## User Defined Types (UDT)

**Example:**
```python
# Create user-defined type
session.execute("""
    CREATE TYPE address (
        street text,
        city text,
        zip_code int,
        country text
    )
""")

session.execute("""
    CREATE TABLE users (
        id int PRIMARY KEY,
        name text,
        home_address frozen<address>,
        work_address frozen<address>
    )
""")

# UDTs are represented as dicts in Python
session.execute(
    "INSERT INTO users (id, name, home_address) VALUES (?, ?, ?)",
    {
        "id": 1,
        "name": "Alice",
        "home_address": {
            "street": "123 Main St",
            "city": "New York",
            "zip_code": 10001,
            "country": "USA"
        }
    }
)

# Query UDT
result = session.execute("SELECT home_address FROM users WHERE id = ?", {"id": 1})
address = result.first_row()[0]
print(f"Address: {address['street']}, {address['city']}")
```

## NULL Values

All CQL types can be NULL. In Python, NULL is represented as `None`:

```python
session.execute("""
    CREATE TABLE users (
        id int PRIMARY KEY,
        email text,
        phone text
    )
""")

# Insert with NULL value
session.execute(
    "INSERT INTO users (id, email, phone) VALUES (?, ?, ?)",
    {"id": 1, "email": "alice@example.com", "phone": None}  # phone is NULL
)

# Query NULL
result = session.execute("SELECT phone FROM users WHERE id = ?", {"id": 1})
phone = result.first_row()[0]
if phone is None:
    print("Phone number not set")
```

## Type Conversion Summary

```python
# Python to CQL
values = {
    "int_val": 42,                          # int -> int
    "float_val": 3.14,                      # float -> double
    "str_val": "hello",                     # str -> text
    "bool_val": True,                       # bool -> boolean
    "bytes_val": b'\x00\x01',               # bytes -> blob
    "list_val": [1, 2, 3],                  # list -> list<int>
    "dict_val": {"a": 1, "b": 2},           # dict -> map<text, int>
    "none_val": None,                       # None -> NULL
}

# All values are automatically converted when executing queries
session.execute("INSERT INTO table (...) VALUES (...)", values)
```

## Best Practices

### 1. Use Appropriate Types

```python
# ✅ DO: Use correct type
session.execute("""
    CREATE TABLE timestamps (
        id int PRIMARY KEY,
        created_at timestamp  -- Use timestamp for dates
    )
""")

# ❌ DON'T: Store timestamps as text
session.execute("""
    CREATE TABLE bad_timestamps (
        id int PRIMARY KEY,
        created_at text  -- Harder to query, sort
    )
""")
```

### 2. Collections Limitations

```python
# ✅ DO: Keep collections small
session.execute(
    "INSERT INTO users (id, tags) VALUES (?, ?)",
    {"id": 1, "tags": ["tag1", "tag2", "tag3"]}  # Small list
)

# ❌ DON'T: Store huge collections
# Collections are loaded entirely into memory
# Better to use separate table for large collections
```

### 3. Frozen Collections for Keys

```python
# ✅ DO: Use frozen for complex keys
session.execute("""
    CREATE TABLE data (
        id frozen<list<int>> PRIMARY KEY,
        value text
    )
""")
```

### 4. NULL Handling

```python
# Always check for None
result = session.execute("SELECT email FROM users WHERE id = ?", {"id": 1})
row = result.first_row()
if row:
    email = row[0]
    if email is not None:
        print(f"Email: {email}")
    else:
        print("No email set")
```
