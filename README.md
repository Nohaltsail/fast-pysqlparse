# fast-pysqlparse: High-Performance SQL Parsing Library

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Language](https://img.shields.io/badge/language-Python%20%7C%20C++17-blue)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-green)]()


[README.md (Chinese)](https://github.com/Nohaltsail/fast-pysqlparse/blob/main/README_CN.md)

A high-performance, cross-platform SQL parsing library, designed to handle the most complex SQL queries with ease.

## Overview

This library provides a robust set of tools for parsing and analyzing SQL statements. Built with a core engine in C++17 for maximum performance, it offers native Python bindings, making it the ideal choice for data-intensive applications where speed and accuracy are critical.

It excels at parsing extremely long SQL statements and queries with deeply nested subqueries, delivering performance far superior to pure-Python alternatives.

## Features

- **Fast SQL Parsing**: Leverages a high-performance C++17 core to parse SQL statements rapidly
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

#### Test 1: Comparison with sqlparse/sqlglot (1359 char SQL, 100 iterations)
| Parser | Total Time | Avg per Parse | Speedup              |
|--------|-----------|---------------|----------------------|
| **fast-pysqlparse** | 0.0170s | 0.17ms | **1.0 x** (baseline) |
| sqlparse | 1.3040s | 13.04ms | **75 x** faster      |
| sqlglot | 0.4283s | 4.28ms | **25 x** faster      |

#### Test 2: 5000 Iterations
- SQL Length: 600+ characters
- Total Time: 0.60s
- **PPS (Parses Per Second): 8000+**
- Average per parse: 0.1ms~0.15ms

#### Test 3: 10 Million Character SQL
- SQL Length: 10,000,000 characters
- Total Time: 1.40s
- **CPS (Characters Per Second): ~7,500,000**
- Parse successful!

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
from fastsqlparse import Parsed
from fastsqlparse.statement import ParsedQuery

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

    # Tokenization - returns list of tuples containing (value, type, position)
    tokens = ParsedQuery.tokenize(sql)  # Get tuple list of token information (value, type, position)

    # Alternative tokenization - returns list of token objects with attributes
    token_obj_list = sql_stmt.tokens()  # Get object list of token information

    # Generate and print Abstract Syntax Tree (AST) in JSON format
    print(sql_stmt.AST())  # Get JSON structure of the SQL statement

    # Extract table lineage/dependencies from the query
    src_tables = ParsedQuery.parse_dependence(sql)  # Get source tables (dependencies) of the query

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

Apache-2.0

