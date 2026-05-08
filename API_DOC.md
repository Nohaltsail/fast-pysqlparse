# fast-pysqlparse API Documentation and Usage Guide

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Classes](#core-classes)
- [Feature Demonstrations](#feature-demonstrations)
- [Performance Comparison](#performance-comparison)
- [API Reference](#api-reference)

---

## Installation

```bash
pip install fast-pysqlparse
```

---

## Quick Start

```python
from fastsqlparse import Parsed, ParsedQuery

# Parse SQL
sql = "SELECT * FROM users WHERE age > 18"
parsed = Parsed(sql)

# Get parsing results
query = parsed.parsedforest[0]
print(query.sources)    # Data sources
print(query.columns)    # Column information
print(query.format())   # Formatted output
```

---

## Core Classes

### 1. Parsed - Main SQL Parser Class

**Function**: Parse any SQL statement (SELECT, INSERT, UPDATE, DELETE, CREATE, etc.)

**Parameters**:
- `sql_statements` (str): SQL statement string
- `file` (str, optional): SQL file path
- `name` (str, optional): Name identifier for the parsed content
- `pure` (bool, default=False): Whether to ignore comments

**Main Attributes and Methods**:
- `parsedforest`: Returns list of parsed statements
- `statements`: All SQL statements
- `tokens()`: Get lexical tokens
- `AST()`: Get abstract syntax tree (JSON format)
- `format(indent)`: Format SQL
- `content()`: Get original SQL content
- `name`: SQL statement name

**Example**:
```python
from fastsqlparse import Parsed

sql = "SELECT u.id, u.name FROM users u WHERE u.age > 18"
parsed = Parsed(sql)

# Get parse tree
items = parsed.parsedforest

# Format
formatted = parsed.format(indent="  ")

# Get AST
ast_json = parsed.AST()

# Get Tokens
tokens = parsed.tokens()
```

---

### 2. ParsedQuery - SELECT Query Parser

**Function**: Specialized parser for SELECT queries, extracts query clauses and metadata

**Parameters**:
- `statement` (str): SELECT statement
- `name` (str): Query name
- `pure` (bool, default=False): Whether to remove comments

**Main Attributes**:
- `sources`: List of data sources (tables from FROM/JOIN)
- `columns`: List of selected columns
- `clause_select`: SELECT clause content
- `clauses`: List of clauses
  - FROM clause content
  - WHERE clause content
  - GROUP BY/HAVING clause
  - ORDER BY clause
  - LIMIT clause
- `parent`: Parent Parsed object
- `cte`: CTE mapping dictionary
- `unions`: List of UNION queries
- `subquery`: Subquery information
- `level`: Nesting level

**Main Methods**:
- `format(indent, init_indent)`: Format query
- `ast()`: Generate AST
- `tokens()`: Get Tokens
- `tokenize(statement)`: Static method for fast lexical analysis

**Example**:
```python
from fastsqlparse import ParsedQuery

sql = """
SELECT u.user_id, COUNT(o.order_id) as cnt
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
WHERE u.status = 'active'
GROUP BY u.user_id
HAVING cnt > 5
ORDER BY cnt DESC
LIMIT 10
"""

query = ParsedQuery(sql, "user_orders")

# Extract information
print("Sources:", query.sources)
print("Columns:", query.columns)
for i, clause in enumerate(query.clauses):
    if clause.part == "CLAUSE_FROM":
        print(f"FROM clause: {clause.clause}")
    elif clause.part == "CLAUSE_WHERE":
        print(f"WHERE condition: {clause.clause}")
    elif clause.part == "CLAUSE_AGGREGATION":
        print(f"GROUP BY: {clause.clause}")
    elif clause.part == "CLAUSE_SORT":
        print(f"ORDER BY: {clause.clause}")
    elif clause.part == "CLAUSE_LIMIT":
        print(f"LIMIT: {clause.clause}")

# Fast tokenizer
tokens = ParsedQuery.tokenize(sql)
for token_type, token_value, pos in tokens[:5]:
    print(f"{token_type}: {token_value}")
```

---

### 3. ParsedCTE - Common Table Expression Parser

**Function**: Parse WITH clauses (CTE)

**Parameters**:
- `statement` (str): WITH statement
- `pure` (bool, default=False): Whether to remove comments
- `name` (str, optional): CTE name

**Main Attributes**:
- `raw`: Raw CTE statement
- `units`: List of CTE statements
- `name`: CTE name

**Main Methods**:
- `format(indent, init_indent)`: Format CTE
- `ast()`: Generate AST
- `tokenize(statement)`: Static method for fast lexical analysis

**Example**:
```python
from fastsqlparse import ParsedCTE, ParsedQuery

sql = """
WITH RECURSIVE cte AS (
    SELECT 1 as n
    UNION ALL
    SELECT n + 1 FROM cte WHERE n < 10
)
"""
cte = ParsedCTE(sql)
print("CTE statements:", cte.units)
print("Formatted:\n", cte.format())

sql = """
WITH RECURSIVE cte AS (
    SELECT 1 as n
    UNION ALL
    SELECT n + 1 FROM cte WHERE n < 10
)
SELECT * FROM cte
"""

ctes = ParsedQuery(sql, 'test').cte
for cte_name in ctes:
    print("CTE name:", cte_name)
    print("CTE statement:", ctes[cte_name].format())
```

---

### 4. ParsedInsert - INSERT Statement Parser

**Function**: Parse INSERT statements, supports both VALUES and SELECT methods

**Parameters**:
- `statement` (str): INSERT statement
- `pure` (bool, default=False): Whether to remove comments

**Main Attributes**:
- `name`: Target table name
- `columns`: List of columns to insert
- `values`: Values to insert
- `query`: Query object (for INSERT...SELECT)
- `query_load`: Whether there is a query load
- `main_stmt`: Main statement
- `cte_stmt`: CTE statement
- `query_stmt`: Query statement

**Main Methods**:
- `format(indent, init_indent)`: Format
- `ast()`: Generate AST
- `tokens()`: Get Tokens
- `tokenize(statement)`: Static method for fast lexical analysis

**Example**:
```python
from fastsqlparse import ParsedInsert

sql1 = "INSERT INTO users (id, name) VALUE (1, 'Alice')"
insert1 = ParsedInsert(sql1)
print("Table name:", insert1.name)
print("Columns:", insert1.columns)
print("Values:", insert1.values)

# SELECT method (with CTE)
sql2 = """
INSERT INTO summary (product_id, total)
WITH stats AS (
    SELECT product_id, SUM(amount) as total
    FROM orders
    GROUP BY product_id
)
SELECT product_id, total FROM stats sts
"""
insert2 = ParsedInsert(sql2)
print("Table name:", insert2.name)
print("Has query:", insert2.query_load)
if insert2.query:
    for source in insert2.query.sources:
        print("Clause:", source.raw)
        print("Table:", source.table)
        print("Alias:", source.alias)

```

---

### 5. Other Parser Classes

#### ParsedView - VIEW Parser
```python
from fastsqlparse import ParsedView

sql = "CREATE VIEW active_users AS SELECT * FROM users WHERE status='active'"
view = ParsedView(sql)
```

#### ParsedUpdate - UPDATE Parser
```python
from fastsqlparse import ParsedUpdate

sql = "UPDATE users SET status='inactive' WHERE last_login < '2023-01-01'"
update = ParsedUpdate(sql)
```

#### ParsedDelete - DELETE Parser
```python
from fastsqlparse import ParsedDelete

sql = "DELETE FROM logs WHERE created_at < '2023-01-01'"
delete = ParsedDelete(sql)
```

#### ParsedCreate - CREATE TABLE Parser
```python
from fastsqlparse import ParsedCreate

sql = """
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(200)
)
"""
create = ParsedCreate(sql)
```

---

## Feature Demonstrations

### Scenario 1: Basic Query (with Subquery)

```python
from fastsqlparse import Parsed

sql = """
SELECT 
    u.user_id,
    u.username,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.user_id) as order_count
FROM users u
WHERE u.age > 18
ORDER BY u.username
LIMIT 10
"""

parsed = Parsed(sql)
query = parsed.parsedforest[0]

# Extract key information
print("Sources:", query.sources)
print("Columns:", query.columns)
print("SELECT clause:", query.clause_select)
for clause in query.clauses:
    if clause.part == "CLAUSE_FROM":
        print(f"FROM clause: {clause.clause}")
    elif clause.part == "CLAUSE_WHERE":
        print(f"WHERE clause: {clause.clause}")
    elif clause.part == "CLAUSE_SORT":
        print(f"ORDER BY clause: {clause.clause}")
    elif clause.part == "CLAUSE_LIMIT":
        print(f"LIMIT clause: {clause.clause}")
```

**Output**:
```
Sources: [<DqlSourceExpr object>]
Columns: [<DqlColumnExpr object>, ...]
SELECT clause: ['u.user_id', 'u.username', '(SELECT COUNT(*) ...) as order_count']
FROM clause: FROM users u
WHERE clause: WHERE u.age > 18
ORDER BY clause: ORDER BY u.username
LIMIT clause: LIMIT 10
```

---

### Scenario 2: Temporary Result Set (Aggregation Query)

```python
from fastsqlparse import Parsed
import json

sql = """
WITH sales_summary AS (
    SELECT 
        product_id,
        SUM(amount) as total_sales,
        AVG(amount) as avg_sales
    FROM sales
    WHERE sale_date >= '2024-01-01'
    GROUP BY product_id
)
SELECT * FROM sales_summary WHERE total_sales > 1000
"""

parsed = Parsed(sql)

# Get Tokens
tokens = parsed.tokens()
print(f"TOKENS count: {len(tokens)}")
print(f"First 5 TOKENS:")
for i, token in enumerate(tokens[:5]):
    print(f"  {i}: {token} (at: {token.value}, type: {token.type}, value: {token.value})")

# Get AST
ast_str = parsed.AST()
ast_obj = json.loads(ast_str)
print(json.dumps(ast_obj, indent=2, ensure_ascii=False)[:500] + "...")
```

---

### Scenario 3: UNION Query + Tokenizer

```python
from fastsqlparse import ParsedQuery

sql = """
WITH region_sales AS (
    SELECT region, SUM(amount) as total
    FROM sales
    GROUP BY region
)
SELECT * FROM region_sales
UNION ALL
SELECT 'TOTAL' as region, SUM(total) FROM region_sales
"""

# Use Tokenizer for fast lexical analysis
tokens = ParsedQuery.tokenize(sql)
print(f"Tokenizer results (first 10 tokens):")
for i, (token_type, token_value, position) in enumerate(tokens[:10]):
    print(f"  {i}: type={token_type}, value='{token_value}', pos={position}")
```

---

### Scenario 4: INSERT INTO ... CTE SELECT

```python
from fastsqlparse import ParsedInsert

sql = """
INSERT INTO summary_table (product_id, total_amount, avg_amount)
WITH product_stats AS (
    SELECT 
        product_id,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount
    FROM orders
    GROUP BY product_id
)
SELECT product_id, total_amount, avg_amount
FROM product_stats
"""

insert = ParsedInsert(sql)

print("Target table name:", insert.name)
print("Insert columns:", insert.columns)
print("Has query load:", insert.query_load)
if insert.query:
    print("Query object type:", type(insert.query))
    print("Query sources:", insert.query.sources)
```

---

### Scenario 5: Handle Comments and Formatting

```python
from fastsqlparse import Parsed, strip_note

sql = """
-- This is the main comment for user query
SELECT 
    u.user_id,  -- User ID
    u.username  -- Username
FROM users u  /* User table */
WHERE u.status = 'active'  -- Only active users
"""

# Format with comments preserved
parsed_with_comments = Parsed(sql, pure=False)
print("Formatted result with comments:")
print(parsed_with_comments.format())

# Format with comments removed
parsed_pure = Parsed(sql, pure=True)
print("\nFormatted result without comments:")
print(parsed_pure.format())

# Only remove comments (without formatting)
stripped = strip_note(sql)
print("\nOnly remove comments:")
print(stripped)
```

---

## Performance Comparison

### Test Environment
- SQL length: 1359 characters
- Test iterations: 100 times

### Performance Results

| Parser | Total Time (100 iterations) | Average per Parse | Relative Speed |
|--------|---------------------------|-------------------|----------------|
| **fast-pysqlparse** | 0.0170s | 0.17ms | **1.0x** (baseline) |
| sqlparse | 1.3040s | 13.04ms | **76.75x** faster |
| sqlglot | 0.4283s | 4.28ms | **25.21x** faster |

### Large-Scale Tests

#### Test 1: 5000 Iterations
- SQL length: 639 characters
- Total time: 0.6084s
- **PPS (Parses Per Second): 8218.88**
- Average per parse: 0.1217ms

#### Test 2: 10 Million Character SQL
- SQL length: 10,500,998 characters
- Total time: 1.4085s
- **CPS (Characters Per Second): 7,455,540**
- Parse successful!

---

## API Reference

### Utility Functions

#### `strip_note(sql: str) -> str`
Remove comments from SQL

```python
from fastsqlparse import strip_note

sql = "SELECT * FROM users -- comment"
clean = strip_note(sql)
# Result: "SELECT * FROM users"
```

#### `format(sql: str, indent: str = "    ") -> str`
Format SQL statement

```python
from fastsqlparse import format

sql = "SELECT * FROM users WHERE id=1"
formatted = format(sql, "query", indent="  ")
```

#### `tokenize(sql: str) -> List[Tuple[str, str, int]]`
Lexical analysis

#### `tokenize_query(sql: str) -> List[Tuple[str, str, int]]`
Fast lexical analysis for SELECT statements

```python
from fastsqlparse import tokenize_query

tokens = tokenize_query("SELECT * FROM users")
```

#### `tokenize_cte(sql: str) -> List[Tuple[str, str, int]]`
Fast lexical analysis for WITH statements

#### `tokenize_insert(sql: str) -> List[Tuple[str, str, int]]`
Fast lexical analysis for INSERT statements

#### `tokenize_update(sql: str) -> List[Tuple[str, str, int]]`
Fast lexical analysis for UPDATE statements

#### `tokenize_delete(sql: str) -> List[Tuple[str, str, int]]`
Fast lexical analysis for DELETE statements

#### `tokenize_view(sql: str) -> List[Tuple[str, str, int]]`
Fast lexical analysis for VIEW statements

---

### Token Structure

Each Token contains the following attributes:
- `type`: Token type (KEYWORD, IDENTIFIER, LITERAL, WHITESPACE, etc.)
- `value`: Token value
- `position`: Position in SQL

```python
tokens = parsed.tokens()
for token in tokens:
    print(f"Type: {token.type}, Value: {token.value}, Pos: {token.at}")
```

---

### AST Structure

AST is returned in JSON format, containing:
- Query clauses (SELECT, FROM, WHERE, etc.)
- CTE definitions
- Column information
- Data source information
- Union query information

```python
import json
ast_json_list = parsed.AST()
ast_json_dic = parsed_query.ast()
ast_obj = json.loads(ast_json_dic)
```

---

## Best Practices

### 1. Choose the Right Parser

- **General SQL**: Use `Parsed`
- **SELECT only**: Use `ParsedQuery` (faster)
- **INSERT only**: Use `ParsedInsert`
- **CTE only**: Use `ParsedCTE`

### 2. Performance Optimization

- If you only need lexical information, use the `tokenize()` static method
- Set `pure=True` to skip comment processing and improve speed
- Avoid re-parsing the same SQL, cache parsing results

### 3. Error Handling

```python
from fastsqlparse import Parsed

try:
    parsed = Parsed(invalid_sql)
except Exception as e:
    print(f"Parse failed: {e}")
```

---

## FAQ

### Q1: How to extract table names?
```python
query = parsed.parsedforest[0]
for source in query.sources:
    print(source.table)  # or check source attributes
```

### Q2: How to handle multi-statement SQL?
```python
parsed = Parsed("SELECT * FROM t1; SELECT * FROM t2;")
for stmt in parsed.parsedforest:
    print(stmt)
```

### Q3: How to get subquery information?
```python
query = parsed.parsedforest[0]
if query.subquery:
    for subq in query.subquery:
        print(subq)
```

---

## GitHub Repository

https://github.com/Nohaltsail/fast-pysqlparse

## License

Apache-2.0
