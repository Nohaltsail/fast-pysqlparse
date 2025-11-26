SQL Parser Library:
A high-performance, cross-platform SQL parsing library, designed to handle the most complex SQL queries with ease.

Overview:

This library provides a robust set of tools for parsing and analyzing SQL statements. Built with a core engine in C++17 for maximum performance, it offers native Python bindings, making it the ideal choice for data-intensive applications where speed and accuracy are critical.

It excels at parsing extremely long SQL statements and queries with deeply nested subqueries, delivering performance far superior to pure-Python alternatives.

Features:

Fast SQL Parsing: Leverages a high-performance C++17 core to parse SQL statements rapidly.

Cross-Platform: Compiled into native extensions (.pyd for Windows, .so for Linux/macOS).

Comprehensive SQL Support: Supports a wide range of SQL statements, including:

        SELECT (with complex JOIN, WHERE, GROUP BY, sub query, etc.)
        INSERT
        Data Definition Language (CREATE, ALTER, DROP)
        VIEW
        DELETE
        UPDATE
        Common Table Expressions (CTEs), including nested CTEs.
        
Abstract Syntax Tree (AST): Generates a detailed JSON representation of the parsed SQL AST for easy traversal and analysis.

SQL Formatting: Automatically reformats messy SQL into a clean, readable structure.

Table Lineage Parsing: Automatically traces and reveals the source-to-target relationships between tables (data lineage).

Tokenization: Breaks down SQL statements into their fundamental tokens for lexical analysis.

Python API: A clean and intuitive Python library built around the high-speed native extension.

Performance:
This library is engineered for speed. By moving the computationally intensive parsing work to a native C++ layer, it significantly outperforms pure-Python parsing libraries, especially when dealing with large, complex SQL scripts.

Installation:

From Source:

    Clone the repository: git clone https://github/Nohaltsail/fast-pysqlparse.git
    Build：python setup.py bdist_wheel
    Install(if you build with Python3.10): cd dist && pip install pysqlparse-0.6.3-cp310-cp310-win_amd64.whl

Quick Start
```python
from pysqlparse import Sql
import time

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
    (SELECT SUM(gross_sales) FROM monthly_sales WHERE year = ms.year AND month = ms.month) AS total_monthly_sales,
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
    (SELECT SUM(total_sales) FROM category_sales WHERE year = cs.year AND month = cs.month) AS total_monthly_sales,
    cs.total_sales / NULLIF((SELECT SUM(total_sales) FROM category_sales WHERE year = cs.year AND month = cs.month), 0) * 100 AS sales_percentage,
    NULL AS overall_avg_order_value
FROM category_sales cs
LIMIT 50, 100"""

    sql_len = len(sql)
    print("sql length: ", sql_len)
    sql_stmt = Sql(sql)
```

Contributing:
Contributions are welcome! Please feel free to submit pull requests, report bugs, or suggest new features.

