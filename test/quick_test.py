from fastsqlparse import Parsed, ParsedQuery, Dialects, DialectType

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

    # parse sql statements to SQL object (ParsedSQL remains a legacy alias of Parsed)
    # dialect selects SQL dialect (default "ansi"; supports mysql/postgresql/sqlite/doris)
    sql_stmt = Parsed(sql, dialect=Dialects.MYSQL.value)
    # Format and print the SQL statement with proper indentation
    print(sql_stmt.format())  # Output formatted SQL statement

    # Tokenization - returns list of tuples containing (token_value, token_type, position)
    # tokenize accepts a DialectType (default DialectType.ANSI)
    tokens = ParsedQuery.tokenize(sql, dialect=DialectType.MYSQL)  # Get tuple list of token information (token_value, token_type, position)

    # Alternative tokenization - returns list of token objects with attributes
    token_obj_list = sql_stmt.tokens()  # Get object list of token information

    # Generate and print Abstract Syntax Tree (AST) in JSON format
    print(sql_stmt.AST())  # Get JSON structure of the SQL statement

    # Extract table lineage/dependencies from the query
    src_tables = ParsedQuery.parse_dependence(sql, dialect="mysql")  # Get source tables (dependencies) of the query
