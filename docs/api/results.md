# Results API Reference

## QueryResult

### Overview

`QueryResult` represents the result of a CQL query execution.

### Properties

Results are returned from `execute()`, `query()`, `execute_prepared()`, and `batch()` methods.

### Methods

#### `rows() -> List[Row]`

Returns all rows as a list.

**Returns:** List of Row objects

**Example:**
```python
result = session.execute("SELECT * FROM users")
rows = result.rows()

for row in rows:
    print(row.columns())
```

#### `first_row() -> Optional[Row]`

Returns the first row or None if no rows.

**Returns:** First Row or None

**Example:**
```python
result = session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
row = result.first_row()

if row:
    print("User found:", row.columns())
else:
    print("User not found")
```

#### `single_row() -> Row`

Returns the single row from the result.

**Returns:** The single Row

**Raises:** `ValueError` if result doesn't contain exactly one row

**Example:**
```python
result = session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})

try:
    row = result.single_row()
    print("User:", row.columns())
except ValueError as e:
    print(f"Error: {e}")  # Not exactly one row
```

#### `first_row_typed() -> Optional[Dict[str, Any]]`

Returns the first row as a dictionary.

**Returns:** Dictionary of column values or None

**Example:**
```python
result = session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
user_dict = result.first_row_typed()

if user_dict:
    print(f"Name: {user_dict.get('name')}")
    print(f"Email: {user_dict.get('email')}")
```

#### `rows_typed() -> List[Dict[str, Any]]`

Returns all rows as dictionaries.

**Returns:** List of dictionaries

**Example:**
```python
result = session.execute("SELECT id, name, email FROM users")
users = result.rows_typed()

for user in users:
    print(f"ID: {user['id']}, Name: {user['name']}")
```

#### `col_specs() -> List[Dict[str, Any]]`

Returns column specifications/metadata.

**Returns:** List of column specification dictionaries

**Example:**
```python
result = session.execute("SELECT * FROM users")
specs = result.col_specs()

for spec in specs:
    print(f"Column: {spec['name']}, Type: {spec['typ']}")
```

#### `tracing_id() -> Optional[str]`

Returns the tracing ID if tracing was enabled.

**Returns:** Tracing ID as string or None

**Example:**
```python
from rsylla import Query

query = Query("SELECT * FROM users").with_tracing(True)
result = session.query(query)

trace_id = result.tracing_id()
if trace_id:
    print(f"Query trace: {trace_id}")
    # Use trace_id to query system_traces tables
```

#### `warnings() -> List[str]`

Returns any warnings from the query.

**Returns:** List of warning strings

**Example:**
```python
result = session.execute("SELECT * FROM large_table")
warnings = result.warnings()

if warnings:
    for warning in warnings:
        print(f"Warning: {warning}")
```

### Iteration Support

QueryResult supports iteration:

```python
result = session.execute("SELECT * FROM users")

# Iterate directly
for row in result:
    print(row.columns())

# Or convert to list first
all_rows = list(result)
```

### Length and Boolean

```python
result = session.execute("SELECT * FROM users")

# Get number of rows
row_count = len(result)
print(f"Found {row_count} rows")

# Boolean check
if result:
    print("Query returned rows")
else:
    print("No rows returned")
```

### Complete Examples

#### Processing Large Result Sets

```python
from rsylla import Query

# Query with paging
query = Query("SELECT * FROM large_table").with_page_size(1000)
result = session.query(query)

print(f"Processing {len(result)} rows")

for i, row in enumerate(result, 1):
    data = row.columns()
    # Process row
    if i % 1000 == 0:
        print(f"Processed {i} rows...")
```

#### Checking Query Results

```python
result = session.execute("SELECT * FROM users WHERE id = ?", {"id": 999})

# Multiple ways to check results
if not result:
    print("No user found")
elif len(result) == 0:
    print("No user found")
elif result.first_row() is None:
    print("No user found")
else:
    user = result.first_row()
    print(f"Found user: {user.columns()}")
```

#### Using Column Metadata

```python
result = session.execute("SELECT * FROM users")

# Get column information
col_specs = result.col_specs()
print("Table columns:")
for spec in col_specs:
    print(f"  {spec['name']}: {spec['typ']}")

# Process rows with column names
rows_dict = result.rows_typed()
for row in rows_dict:
    for col_name in row.keys():
        print(f"{col_name}: {row[col_name]}")
```

---

## Row

### Overview

`Row` represents a single row from a query result.

### Methods

#### `columns() -> List[Any]`

Returns all column values as a list.

**Returns:** List of column values

**Example:**
```python
result = session.execute("SELECT id, name, email FROM users")

for row in result:
    id, name, email = row.columns()
    print(f"{id}: {name} ({email})")
```

#### `as_dict() -> Dict[str, Any]`

Converts the row to a dictionary.

**Returns:** Dictionary of column name to value

**Note:** Column names are generated as `col_0`, `col_1`, etc. Use column specs from QueryResult for actual names.

**Example:**
```python
row = result.first_row()
if row:
    row_dict = row.as_dict()
    print(row_dict)
```

#### `get(index: int) -> Any`

Gets a column value by index.

**Parameters:**
- `index`: Zero-based column index

**Returns:** Column value

**Raises:** `IndexError` if index out of range

**Example:**
```python
row = result.first_row()
if row:
    id_value = row.get(0)
    name_value = row.get(1)
    print(f"ID: {id_value}, Name: {name_value}")
```

### Indexing Support

Rows support indexing and negative indices:

```python
row = result.first_row()

# Positive indexing
first_col = row[0]
second_col = row[1]

# Negative indexing
last_col = row[-1]
second_last = row[-2]

# Length
num_columns = len(row)
```

### Complete Examples

#### Destructuring Rows

```python
result = session.execute("SELECT id, name, email, created_at FROM users")

for row in result:
    # Unpack columns
    id, name, email, created_at = row.columns()

    print(f"User {id}:")
    print(f"  Name: {name}")
    print(f"  Email: {email}")
    print(f"  Created: {created_at}")
```

#### Accessing Columns by Index

```python
result = session.execute("SELECT * FROM users WHERE id = ?", {"id": 1})
row = result.first_row()

if row:
    # Access by index
    print(f"Column 0: {row[0]}")
    print(f"Column 1: {row[1]}")
    print(f"Last column: {row[-1]}")

    # Iterate columns
    for i in range(len(row)):
        print(f"Column {i}: {row[i]}")
```

#### Handling Optional Rows

```python
def get_user_name(user_id: int) -> Optional[str]:
    result = session.execute(
        "SELECT name FROM users WHERE id = ?",
        {"id": user_id}
    )

    row = result.first_row()
    if row:
        return row[0]  # name column
    return None

# Usage
name = get_user_name(123)
if name:
    print(f"User name: {name}")
else:
    print("User not found")
```

#### Processing Different Row Types

```python
# Wide rows with many columns
result = session.execute("SELECT * FROM user_stats")

for row in result:
    columns = row.columns()

    # Process based on number of columns
    if len(row) > 10:
        # Full user stats
        process_full_stats(columns)
    else:
        # Partial stats
        process_partial_stats(columns)
```

### Type Conversions

Rows automatically convert CQL types to Python types:

```python
result = session.execute("""
    SELECT
        id,              -- int
        name,            -- text
        balance,         -- decimal
        is_active,       -- boolean
        tags,            -- list<text>
        metadata,        -- map<text, text>
        created_at       -- timestamp
    FROM users
    WHERE id = ?
""", {"id": 1})

row = result.first_row()
if row:
    id, name, balance, is_active, tags, metadata, created_at = row.columns()

    print(f"ID: {id} (int)")
    print(f"Name: {name} (str)")
    print(f"Balance: {balance} (Decimal/str)")
    print(f"Active: {is_active} (bool)")
    print(f"Tags: {tags} (list)")
    print(f"Metadata: {metadata} (dict)")
    print(f"Created: {created_at} (int timestamp)")
```
