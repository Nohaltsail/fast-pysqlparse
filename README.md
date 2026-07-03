# fast-pysqlparse: High-Performance SQL Parsing Library

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Version](https://img.shields.io/badge/version-0.8-blue)]()
[![Language](https://img.shields.io/badge/language-Python%20%7C%20C++17-blue)]()
[![License](https://img.shields.io/badge/license-MIT-purple)]()


[README.md (Chinese)](https://github.com/Nohaltsail/fast-pysqlparse/blob/main/README_CN.md)

A high-performance, cross-platform, lightweight SQL parsing library whose core trait is **speed** — built on a C++17 core with native Python bindings, it rapidly performs structured parsing of SQL, especially statements with highly complex structure and deep nesting.

## Overview

fast-pysqlparse aims to overcome the performance and capability limits of traditional Python SQL parsers. By moving compute-intensive parsing into a native C++ layer, it maintains fast parsing even on large, deeply nested, structurally complex SQL.

The parser primarily parses ANSI-style SQL. For statements with a specific dialect, specifying the dialect is recommended; supported dialects: MySQL, PostgreSQL, SQLite, Doris.

## Features

- **Fast SQL Parsing**: Leverages a high-performance C++17 core to parse SQL statements rapidly
- **Structured Parsing**: Oriented toward complex structure and deep nesting, especially statements mixing CTEs with SELECT/INSERT/VIEW
- **Cross-Platform**: Compiled into native extensions (.pyd for Windows, .so for Linux)
- **Comprehensive SQL Support**: Supports a wide range of SQL statements, including:
  - SELECT (with complex JOIN, WHERE, GROUP BY, subqueries, etc.)
  - INSERT
  - Data Definition Language (CREATE)
  - VIEW
  - DELETE
  - UPDATE
  - Common Table Expressions (CTEs), including nested CTEs
- **Abstract Syntax Tree (AST)**: Generates a detailed JSON representation of the parsed SQL AST for easy traversal and analysis
- **SQL Formatting**: Automatically reformats messy SQL into a clean, readable structure
- **Table Lineage Parsing**: Automatically traces and reveals the source-to-target relationships between tables (data lineage)
- **Tokenization**: Breaks down SQL statements into their fundamental tokens for lexical analysis
- **Python API**: A clean and intuitive Python library built around the high-speed native extension

## Performance

This library is engineered for speed. By moving the computationally intensive parsing work to a native C++ layer, it significantly outperforms pure-Python parsing libraries, especially when dealing with large, complex SQL scripts.

### Benchmark Results

#### Test 1: 5000 Iterations
- SQL Length: 639 characters
- Total Time: 0.48s
- **PPS (Parses Per Second): ~10300**
- Average per parse: ~0.097ms

#### Test 2: 10 Million Character SQL
- SQL Length: 10,500,998 characters
- Total Time: 0.54s
- **CPS (Characters Per Second): ~19,500,000**
- Parse successful!

#### Test 3: Python-Only Comparison on ~10M PostgreSQL SQL (No C Benchmark)

Benchmark script: `test/python_parsers_10m.py`

| Parser | Avg Time | CPS |
|--------|----------|-----|
| **fastsqlparse** | 0.7394s | 13,524,892.44 |
| pglast | 4.8541s | 2,060,217.57 |
| sqlglot (postgres) | 20.5364s | 486,963.12 |
| sqlparse | 84.9591s | 117,709.35 |

Notes:
- SQL size: 10,000,484 chars
- Runs per parser: 1
- Results source: results of `test/python_parsers_10m.py`

## Installation

```shell
pip install fast-pysqlparse
```

From Source:
    
    git clone https://github.com/Nohaltsail/fast-pysqlparse.git
    cd fast-pysqlparse
    pip install build
    python -m build
    cd dist
    pip install fast_pysqlparse-*.whl

### Quick Start


```python
from fastsqlparse import Parsed, ParsedQuery

if __name__ == '__main__':
    sql = """

-- main query
SELECT 
    'Monthly Sales Report' AS report_type,
    ms.year,
    ms.month,
    ms.region,
    ms.customer_segment,
    ms.unique_customers,
    ms.total_orders,
    ms.gross_sales,
    ms.avg_order_value,
    ms.cancelled_orders,
    (SELECT SUM(gross_sales) FROM sub_monthly_sales WHERE year = ms.year AND month = ms.month) AS total_monthly_sales,
    ms.gross_sales / NULLIF((SELECT SUM(gross_sales) FROM monthly_sales WHERE year = ms.year AND month = ms.month), 0) * 100 AS sales_percentage,
    (SELECT AVG(avg_order_value) FROM monthly_sales WHERE year = ms.year AND month = ms.month) AS overall_avg_order_value
FROM monthly_sales ms

UNION ALL

SELECT 
    'Category Performance' AS report_type,
    cs.year,
    cs.month,
    NULL AS region,
    cs.category_name AS customer_segment,
    cs.unique_buyers AS unique_customers,
    cs.order_count AS total_orders,
    cs.total_sales AS gross_sales,
    cs.total_sales / NULLIF(cs.order_count, 0) AS avg_order_value,
    NULL AS cancelled_orders,
    (SELECT SUM(total_sales) FROM sub_category_sales WHERE year = cs.year AND month = cs.month) AS total_monthly_sales,
    cs.total_sales / NULLIF((SELECT SUM(total_sales) FROM category_sales WHERE year = cs.year AND month = cs.month), 0) * 100 AS sales_percentage,
    NULL AS overall_avg_order_value
FROM category_sales cs
LIMIT 50, 100"""

    sql_len = len(sql)
    print("sql length: ", sql_len)

    # parse sql statements to SQL object
    sql_stmt = Parsed(sql)
    # Format and print the SQL statement with proper indentation
    print(sql_stmt.format())  # Output formatted SQL statement

    # Tokenization - returns list of tuples containing (token_value, token_type, position)
    tokens = ParsedQuery.tokenize(sql)  # Get tuple list of token information (token_value, token_type, position)

    # Alternative tokenization - returns list of token objects with attributes
    token_obj_list = sql_stmt.tokens()  # Get object list of token information

    # Generate and print Abstract Syntax Tree (AST) in JSON format
    print(sql_stmt.AST())  # Get JSON structure of the SQL statement

    # Extract table lineage/dependencies from the query
    src_tables = ParsedQuery.parse_dependence(sql)  # Get source tables (dependencies) of the query

```

### Comment Handling (`pure`)

`pure` controls SQL comment handling in parser constructors such as `Parsed`,
`ParsedQuery`, `ParsedInsert`, `ParsedCTE`, `ParsedUpdate`, `ParsedDelete`,
`ParsedView`, and `ParsedCreate`.

- `pure=False` (default): keep comments in parsing/formatting output.
- `pure=True`: strip `--` and `/* ... */` comments before parsing; formatted
  output and token results exclude comments, and parsing may be faster.

```python
from fastsqlparse import Parsed

parsed_keep = Parsed(sql, pure=False)  # preserve comments
parsed_clean = Parsed(sql, pure=True)  # strip comments before parse
```

### Dialects (`dialect`)

`dialect` selects the SQL dialect for parsing and lexical analysis (default
`"ansi"`). Every parser constructor accepts `dialect` as a string; `tokenize`
classmethods and `ParsedQuery.parse_dependence` accept a `DialectType`
(default `DialectType.ANSI`).

Supported dialects: `ansi`, `mysql`, `postgresql`, `sqlite`, `doris`
(see the `Dialects` enum and the `DIALECT_*` constants in `fastsqlparse.conf`).

```python
from fastsqlparse import Parsed, ParsedQuery, Dialects, DialectType

parsed = Parsed(sql, dialect=Dialects.MYSQL.value)          # "mysql"
query = ParsedQuery(sql, "q", dialect="postgresql")
ParsedQuery.tokenize(sql, dialect=DialectType.MYSQL)        # typed DialectType
ParsedQuery.parse_dependence(sql, dialect="mysql")
```

## When to Use Which Parser

| **Scenario** | **Parser to Use**  |
|--------------|--------------------|
| SQL statement type is unknown or you don't want to specify the type | `Parsed/ParsedOne` |
| Multiple SQL statements separated by `;` (script execution) | `Parsed`           |
| SELECT / query statement | `ParsedQuery`      |
| INSERT statement | `ParsedInsert`     |
| DELETE statement | `ParsedDelete`     |
| UPDATE statement | `ParsedUpdate`     |
| CREATE TABLE statement | `ParsedCreate`     |
| CREATE VIEW statement | `ParsedView`       |
| CTE (WITH clause) statement | `ParsedCTE`        |

> **Note:** If your SQL contains multiple statements separated by semicolons (e.g., a script with CREATE, INSERT, SELECT), you **must** use `Parsed`. The type-specific parsers are designed for single, known-type statements only.

## Documentation

For complete API documentation, see: [API_DOC.md](https://github.com/Nohaltsail/fast-pysqlparse/blob/main/API_DOC.md)

## Contributing

Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest new features.

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Note on Dynamic Libraries

This project currently distributes precompiled dynamic libraries (`.pyd` and `.so`).
The corresponding C++ source code for these dynamic libraries is temporarily not public and is planned to be opened in a future release.

For the full supplementary notice, see [LICENSE](LICENSE).

**You can also use the dynamic libraries from the source code directly to develop your own SQL parsing library.**

