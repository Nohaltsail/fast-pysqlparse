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

> The parser is primarily tested against MySQL-style SQL. Current supported dialect names are exposed in `fastsqlparse.conf.SUPPORT_DIALECTS`.

```python
from fastsqlparse import Parsed, ParsedQuery

# Parse SQL
sql = "SELECT * FROM users WHERE age > 18"
parsed = Parsed(sql)

# Get parsing results
query = parsed.parsed_forest[0]
print(query.parsed.sources)    # Data sources
print(query.parsed.columns)    # Column information
print(parsed.format())         # Formatted output
```

---

## Core Classes

### 1. Parsed - Main SQL Parser Class

**Function**: Parse any SQL statement (SELECT, INSERT, UPDATE, DELETE, CREATE, etc.)

**Parameters**:
- `sql_statements` (str): SQL statement string
- `file` (str, optional): SQL file path
- `name` (str, optional): Name identifier for the parsed content
- `pure` (bool, default=False): Controls SQL comment handling. `True` strips `--` and `/* ... */` comments before parsing, so formatted output and tokens exclude comments and parsing may be faster; `False` preserves comments.

**Main Attributes and Methods**:
- `parsed_forest`: Returns list of parsed statements
- `statements`: All SQL statements
- `tokens()`: Get lexical tokens
- `AST()`: Get abstract syntax tree (JSON format)
- `ast()`: Get decoded Python object (equivalent to `json.loads(AST())`)
- `format(indent)`: Format SQL
- `content()`: Get original SQL content
- `name`: SQL statement name

**Example**:
```python
from fastsqlparse import Parsed

sql = "SELECT u.id, u.name FROM users u WHERE u.age > 18"
parsed = Parsed(sql)

# Get parse tree
items = parsed.parsed_forest

# Format
formatted = parsed.format(indent="  ")

# Get AST
ast_json = parsed.AST()

# Get Tokens
tokens = parsed.tokens()
```

---

### 1.1. ParsedOne - Single Statement SQL Parser

**Function**: Parse a single SQL statement, automatically detect type and return corresponding parsed object

**Parameters**:
- `sql_statements` (str): SQL statement string

**Main Attributes**:
- `parsed`: AbstractParsed - Parsed structure object (could be ParsedQuery, ParsedInsert, etc.)
- `type`: str - Statement type ("query", "insert", "update", "delete", "create", "view", etc.)

**Main Methods**:
- `tokens()`: List[Token] - Get token list
- `AST()`: str - Get JSON formatted AST
- `ast()`: dict | list - Get decoded Python object
- `format(indent: str = "    ")`: str - Format SQL

**Example**:
```python
from fastsqlparse import ParsedOne, ParsedQuery

sql = "SELECT * FROM users WHERE age > 18"
parsed = ParsedOne(sql)

if parsed.type == "query":
    query: ParsedQuery = parsed.parsed
    print("Sources:", query.parsed.sources)
    print("Columns:", query.parsed.columns)
elif parsed.type == "insert":
    # Handle INSERT statement
    pass
```

---

### 2. ParsedQuery - SELECT Query Parser

**Function**: Specialized parser for SELECT queries, extracts query clauses and metadata

**Parameters**:
- `statement` (str): SELECT statement
- `name` (str): Query name identifier
- `pure` (bool, default=False): Controls SQL comment handling. `True` strips `--` and `/* ... */` comments before parsing, so formatted output and tokens exclude comments and parsing may be faster; `False` preserves comments.

**Main Attributes**:
- `name`: str - Statement name identifier
- `statement` - Query statement
- `level` - Nesting level
- `super`: str - Parent name identifier
- `parent`: ParsedAbstract - Parent parsed object
- `cte`: CommonTableExpr - Common Table Expression (CTE at SELECT query level). Note: This object differs from ParsedInsert.cte in type, accessible via `.common_tables` and `.expressions` attributes.
  - `common_tables`: List[str] - List of common tables
  - `expressions`: Dict[str, ParsedCTE] - Expression dictionary
- `parsed`: QueryStatement - Parsed structure object
  - Normal SELECT form:
    - `T`: str - statement type, usually `SELECT`
    - `sources`: List[DqlSourceExpr] - List of data sources
    - `columns`: List[DqlColumnExpr] - List of columns
    - `clause_select`: List[str] - SELECT clause content
    - `clauses`: List[DqlClause] - All clauses
    - `subquery`: Dict[str, ParsedQuery] - Subquery dictionary
  - UNION form:
    - `T`: str - statement type, usually `UNIONS`
    - `unions`: List[ParsedQuery | str] - UNION query list

**Main Methods**:
- `format(indent, init_indent)`: Format query
- `ast()`: Generate AST
- `tokens()`: Get Tokens
- `available_cte()`: Get all CTEs available in current query scope. These CTEs typically come from ancestor ParsedQuery/ParsedInsert objects, including WITH clauses defined in current and parent queries. Returns a dictionary with CTE names as keys and ParsedCTE objects as values.
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
parsed = query.parsed

# Extract information
print("Sources:", parsed.sources)
print("Columns:", parsed.columns)
for i, clause in enumerate(parsed.clauses):
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
for token_value, token_type, pos in tokens[:5]:
    print(f"{token_type}: {token_value}")
```

---

### 3. ParsedCTE - Common Table Expression Parser

**Function**: Parse WITH clauses (CTE)

**Parameters**:
- `statement` (str): WITH statement
- `pure` (bool, default=False): Controls SQL comment handling. `True` strips `--` and `/* ... */` comments before parsing, so formatted output and tokens exclude comments and parsing may be faster; `False` preserves comments.
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

query = ParsedQuery(sql, 'test')
if query.cte:
    print("CTEs object:", query.cte)
    # common_tables and expressions are attributes of CommonTableExpr object
    print("common tables:", query.cte.common_tables)
    print("expressions:", query.cte.expressions)
    for cte_name in query.cte.expressions:
        print("CTE name:", cte_name)
        print("CTE statement:", query.cte.expressions[cte_name].format())
```

---

### 4. ParsedInsert - INSERT Statement Parser

**Function**: Parse INSERT statements, supports both VALUES and SELECT methods

**Parameters**:
- `statement` (str): INSERT statement
- `pure` (bool, default=False): Controls SQL comment handling. `True` strips `--` and `/* ... */` comments before parsing, so formatted output and tokens exclude comments and parsing may be faster; `False` preserves comments.

**Main Attributes**:
- `name`: str - Target table name
- `columns`: List[str] - List of columns to insert
- `values`: List[str] - Values to insert
- `query`: ParsedQuery - Query object (for INSERT...SELECT)
- `query_load`: bool - Whether there is a query load
- `main_stmt`: str - Main statement
- `cte`: ParsedWithStmt - CTE parsed object (CTE at INSERT statement level, WITH clause defined before INSERT). Note: This object's attributes differ from ParsedQuery.cte, primarily accessed via `.units` for CTE unit list.
- `cte_stmt`: str - CTE statement
- `query_stmt`: str - Query statement

**Main Methods**:
- `format(indent, init_indent)`: Format
- `ast()`: Generate AST
- `tokens()`: Get Tokens
- `tokenize(statement)`: Static method for fast lexical analysis

**Example**:
```python
from fastsqlparse import ParsedInsert, ParsedQuery

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
# Note: insert2.cte is ParsedWithStmt type, different from query.cte (CommonTableExpr)
if insert2.cte:
    print("INSERT-level CTE units:", insert2.cte.units)
if insert2.query:
    print("Query object type:", type(insert2.query))
    parsed_query: ParsedQuery = insert2.query
    print("parsed_query.parsed:", parsed_query.parsed)
    # parsed_query.cte is CommonTableExpr type with common_tables and expressions attributes
    print("parsed_query.cte:", parsed_query.cte)
    if parsed_query.cte:
        # common_tables and expressions are attributes of CommonTableExpr object
        print("common_tables:", parsed_query.cte.common_tables)
        print("expressions:", parsed_query.cte.expressions)
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
from fastsqlparse import Parsed, ParsedQuery

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

parsed_multi = Parsed(sql)
query: ParsedQuery = parsed_multi.parsed_forest[0]
parsed = query.parsed

# Extract key information
print("parsed:", parsed)
print("Sources:", parsed.sources)
print("Columns:", parsed.columns)
print("SELECT clause:", parsed.clause_select)
print("Subqueries:", parsed.subquery)
for clause in parsed.clauses:
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
parsed: QueryStatement(type=SELECT)

Sources: [DqlSourceExpr(table='users', alias='u')]
Columns: [DqlColumnExpr(name='user_id', table='u'), DqlColumnExpr(name='username', table='u'), ...]
SELECT clause: ['u.user_id', 'u.username', '(SELECT COUNT(*) ...) as order_count']
Subqueries: {'order_count': ParsedQuery(position=45, name='order_count' at 0x...)}
FROM clause: FROM users u
WHERE clause: WHERE u.age > 18
ORDER BY clause: ORDER BY u.username
LIMIT clause: LIMIT 10
```

---

### Scenario 2: Temporary Result Set (Aggregation Query)

```python
from fastsqlparse import ParsedOne, ParsedQuery
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

parsed = ParsedOne(sql)
if parsed.type == "query":
    query: ParsedQuery = parsed.parsed
    print(f"parsed_query: {query}")
    print(f"CTEs: {query.cte}")
    # common_tables and expressions are attributes of CommonTableExpr object
    if query.cte:
        print(f"common tables: {query.cte.common_tables}")
        print(f"expressions: {query.cte.expressions}")

print(f"TOKENS count: {len(parsed.tokens())}")
print(f"First 5 TOKENS:")
for i, token in enumerate(parsed.tokens()[:5]):
    print(token)

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
for i, (token_value, token_type, position) in enumerate(tokens[:10]):
    print(f"  {i}: type={token_type}, value='{token_value}', pos={position}")
```

---

### Scenario 4: INSERT INTO ... CTE SELECT

```python
from fastsqlparse import ParsedInsert, ParsedQuery

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

insert_parsed = ParsedInsert(sql)

print("Target table name:", insert_parsed.name)
print("Insert columns:", insert_parsed.columns)
print("Has query load:", insert_parsed.query_load)
# Note: insert_parsed.cte is ParsedWithStmt type
if insert_parsed.cte:
    print("INSERT-level CTE units:", insert_parsed.cte.units)
if insert_parsed.query:
    print("Query object type:", type(insert_parsed.query))
    print("Query sources:", insert_parsed.query.parsed.sources)
print("insert_parsed.cte:", insert_parsed.cte)

parsed_query: ParsedQuery = insert_parsed.query
print("parsed_query:", parsed_query)
print("parsed_query.parsed:", parsed_query.parsed)
# parsed_query.cte is CommonTableExpr type with common_tables and expressions attributes
print("parsed_query.cte:", parsed_query.cte)
if parsed_query.cte:
    # common_tables and expressions are attributes of CommonTableExpr object
    print("parsed_query.cte.common_tables:", parsed_query.cte.common_tables)
    print("parsed_query.cte.expressions:", parsed_query.cte.expressions)
print("parsed_query.parsed.columns:", parsed_query.parsed.columns)
```

---

### Scenario 5: Handle Comments and Formatting

```python
from fastsqlparse import Parsed, strip_comments

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
stripped = strip_comments(sql)
print("\nOnly remove comments:")
print(stripped)
```

---

## Performance Comparison

### Test Environment
- SQL length: 1359 characters
- Test iterations: 100 times

### Performance Results

test script：`test/python_parsers_10m.py`

| parser             | interval | CPS |
|--------------------|----------|-----|
| **fastsqlparse**   | 1.3054s  | 7,660,928.40 |
| pglast             | 4.3322s  | 2,308,429.85 |
| sqlglot (postgres) | 22.9163s | 436,392.53 |
| sqlparse           | 87.2098s | 114,671.60 |

comment：
- SQL length：10,000,484 chars
- times：1
- result：from `test/benchmark_results/python_parsers_10m.json`


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

#### `strip_comments(sql: str) -> str`
Remove SQL comments from SQL text.

```python
from fastsqlparse import strip_comments

sql = "SELECT * FROM users -- comment"
clean = strip_comments(sql)
# Result: "SELECT * FROM users"
```


#### `format(sql: str, indent: str = "    ") -> str`
Format SQL statement

```python
from fastsqlparse import format

sql = "SELECT * FROM users WHERE id=1"
formatted = format(sql, indent="  ")
```

#### `tokenize(sql: str) -> List[Tuple[str, str, int]]`
Lexical analysis

Returned tuples follow the order `(token_value, token_type, position)`.

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
- `type`: Token type (KEYWORD, IDENTIFIER, NUMBER/STRING, WHITESPACE, etc.)
- `value`: Token value
- `position`: Position in SQL

```python
tokens = parsed.tokens()
for token in tokens:
    print(f"Type: {token.type}, Value: {token.value}, Pos: {token.at}")
```

**Token Types**:
- `KEYWORD`: SQL keywords (SELECT, FROM, WHERE, etc.)
- `IDENTIFIER`: Identifiers (table names, column names, aliases)
- `NUMBER/STRING`: Literals (numbers, strings)
- `WHITESPACE`: Whitespace characters
- `SUBQUERY`: Subquery
- `OPERATOR`: Operators
- `COMMENT`: Comments

---

### Common AST / Type Reference

These names show up repeatedly in parser results and examples:

| Type | Typical fields | Notes |
|------|----------------|-------|
| `DqlSourceExpr` | `table`, `alias` | FROM/JOIN source expression |
| `DqlColumnExpr` | `name`, `table`, `alias` | SELECT / derived column metadata |
| `DqlClause` | `part`, `clause` | Individual query clause node |
| `QueryStatement` | `T`, `sources`, `columns`, `clauses`, `subquery`, `clause_select` or `T`, `unions` | Parsed SELECT or UNION structure |
| `CommonTableExpr` | `common_tables`, `expressions` | SELECT-level CTE container |
| `ParsedWithStmt` | `units` | INSERT-level WITH statement container |

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

Complete AST example for a simple SQL:

```python
import json
from fastsqlparse import Parsed

parsed = Parsed("SELECT a FROM t")
full_ast = json.loads(parsed.AST())
print(json.dumps(full_ast, indent=2, ensure_ascii=False))
```

---

## Best Practices

### 1. Choose the Right Parser

- **General SQL or multi-statements**: Use `Parsed`
- **Single statement auto-detect**: Use `ParsedOne` (recommended)
- **Known SELECT**: Use `ParsedQuery`
- **Known INSERT**: Use `ParsedInsert`
- **CTE only**: Use `ParsedCTE`

### 2. Performance Optimization

- If you only need lexical information, use the `tokenize()` static method
- Set `pure=True` to strip `--` and `/* ... */` comments before parsing; this usually improves speed and keeps formatted output/tokens comment-free
- Avoid re-parsing the same SQL, cache parsing results

### 3. Error Handling

Parsing failures are raised as standard Python exceptions from the binding layer, so `except Exception as e` is sufficient for most applications.

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
from fastsqlparse import ParsedOne, ParsedQuery

parsed = ParsedOne(sql)
if parsed.type == "query":
    query: ParsedQuery = parsed.parsed
    for source in query.parsed.sources:
        print(source.table)  # or check source attributes
```

### Q2: How to handle multi-statement SQL?
```python
from fastsqlparse import Parsed

parsed = Parsed("SELECT * FROM t1; SELECT * FROM t2;")
for stmt in parsed.parsed_forest:
    print(stmt)
```

### Q3: How to get subquery information?
```python
from fastsqlparse import ParsedOne, ParsedQuery

parsed = ParsedOne(sql)
if parsed.type == "query":
    query: ParsedQuery = parsed.parsed
    if query.parsed.subquery:
        for subq_name, subq in query.parsed.subquery.items():
            print(f"Subquery name: {subq_name}")
            print(f"Subquery object: {subq}")
```

### Q4: How to use available_cte() to get available CTEs?
```python
from fastsqlparse import ParsedQuery

sql = """
WITH cte1 AS (SELECT 1 as n)
SELECT * FROM cte1
"""

query = ParsedQuery(sql, 'test')
available_ctes = query.available_cte()
print("Available CTEs:", available_ctes)
```

---

## GitHub Repository

https://github.com/Nohaltsail/fast-pysqlparse

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Note on Dynamic Libraries

This project currently distributes precompiled dynamic libraries (`.pyd` and `.so`).
The corresponding C++ source code for these dynamic libraries is temporarily not public and is planned to be opened in a future release.
