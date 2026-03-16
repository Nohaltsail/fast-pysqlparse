from pysqlparse import sql

statement = """
SELECT * FROM table1
LEFT JOIN table2
WHERE table1.col1 = 1
AND table2.col2 = 2
"""

parsed = sql.Sql(statement)
print(parsed.AST())
print(parsed.format())
