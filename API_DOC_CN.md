# fast-pysqlparse API 文档与使用指南

## 目录
- [安装](#安装)
- [快速开始](#快速开始)
- [核心类说明](#核心类说明)
- [功能演示](#功能演示)
- [性能对比](#性能对比)
- [API参考](#api参考)

---

## 安装

```bash
pip install fast-pysqlparse
```

---

## 快速开始

> 解析器主要针对 MySQL 风格 SQL 进行测试；支持的方言通过 `fastsqlparse.conf` 中的 `Dialects` 枚举暴露（并由 `fastsqlparse` 重新导出）：`ansi`、`mysql`、`postgresql`、`sqlite`、`doris`。通过任意解析器构造函数或 `tokenize`/`parse_dependence` 方法的 `dialect` 参数指定方言（默认 `ansi`）。

```python
from fastsqlparse import Parsed, ParsedQuery, Dialects

# 解析SQL
sql = "SELECT * FROM users WHERE age > 18"
parsed = Parsed(sql, dialect=Dialects.MYSQL.value)

# 获取解析结果
query = parsed.parsed_forest[0]
print(query.parsed.sources)    # 数据源
print(query.parsed.columns)    # 列信息
print(parsed.format())         # 格式化输出
```

---

## 核心类说明

### 1. Parsed - SQL解析器主类

**功能**: 解析任意SQL语句（SELECT、INSERT、UPDATE、DELETE、CREATE等）

**参数**:
- `sql_statements` (str): SQL语句字符串
- `file` (str, optional): SQL文件路径
- `name` (str, optional): 解析内容名称
- `pure` (bool, default=False): 控制 SQL 注释处理。`True` 会在解析前移除 `--` 与 `/* ... */` 注释，因此格式化结果和 tokens 不含注释，且解析可能更快；`False` 保留注释。
- `dialect` (str, default=`"ansi"`): SQL 方言。支持：`ansi`、`mysql`、`postgresql`、`sqlite`、`doris`。可使用 `Dialects.<NAME>.value` 进行类型安全选择。

**主要属性和方法**:
- `parsed_forest`: 返回解析后的语句列表
- `statements`: 所有SQL语句
- `tokens()`: 获取词法单元
- `AST()`: 获取抽象语法树（JSON格式）
- `ast()`: 获取已解析的 Python 对象（等价于 `json.loads(AST())`）
- `format(indent)`: 格式化SQL
- `content()`: 获取原始SQL内容
- `name`: SQL语句名称

**示例**:
```python
from fastsqlparse import Parsed

sql = "SELECT u.id, u.name FROM users u WHERE u.age > 18"
parsed = Parsed(sql)

# 获取解析树
items = parsed.parsed_forest

# 格式化
formatted = parsed.format(indent="  ")

# 获取AST
ast_json = parsed.AST()

# 获取Tokens
tokens = parsed.tokens()
```

---

### 1.1. ParsedOne - 单语句SQL解析器

**功能**: 解析单个SQL语句，自动识别类型并返回对应的解析对象

**参数**:
- `sql_statements` (str): SQL语句字符串
- `dialect` (str, default=`"ansi"`): SQL 方言。支持：`ansi`、`mysql`、`postgresql`、`sqlite`、`doris`。可使用 `Dialects.<NAME>.value` 进行类型安全选择。

**主要属性**:
- `parsed`: AbstractParsed - 解析后的结构对象（可能是ParsedQuery、ParsedInsert等）
- `type`: str - 语句类型（"query", "insert", "update", "delete", "create", "view"等）

**主要方法**:
- `tokens()`: List[Token] - 获取Token列表
- `AST()`: str - 获取JSON格式的AST
- `ast()`: dict | list - 获取已解析的 Python 对象
- `format(indent: str = "    ")`: str - 格式化SQL

**示例**:
```python
from fastsqlparse import ParsedOne, ParsedQuery

sql = "SELECT * FROM users WHERE age > 18"
parsed = ParsedOne(sql)

if parsed.type == "query":
    query: ParsedQuery = parsed.parsed
    print("数据源:", query.parsed.sources)
    print("列:", query.parsed.columns)
elif parsed.type == "insert":
    # 处理INSERT语句
    pass
```

---

### 2. ParsedQuery - SELECT查询解析器

**功能**: 专门解析SELECT查询语句，提取查询子句和元数据

**参数**:
- `statement` (str): SELECT语句
- `name` (str): 查询名称标识
- `pure` (bool, default=False): 控制 SQL 注释处理。`True` 会在解析前移除 `--` 与 `/* ... */` 注释，因此格式化结果和 tokens 不含注释，且解析可能更快；`False` 保留注释。
- `dialect` (str, default=`"ansi"`): SQL 方言。支持：`ansi`、`mysql`、`postgresql`、`sqlite`、`doris`。可使用 `Dialects.<NAME>.value` 进行类型安全选择。

**主要属性**:
- `name`: str - 语句名称标识
- `statement` - 查询语句
- `level` - 嵌套层级
- `super`: str - 父级名称标识
- `parent`: ParsedAbstract - 父级解析对象
- `cte`: CommonTableExpr - 公共表表达式（SELECT查询级别的CTE）。注意：此对象与ParsedInsert.cte类型不同，可通过 `.common_tables` 和 `.expressions` 等属性访问。
  - `common_tables`: List[str] - 公共表列表
  - `expressions`: Dict[str, ParsedCTE] - 表达式字典
- `parsed`: QueryStatement - 解析后的结构对象
  - 普通 SELECT 形态：
    - `T`: str - 语句类型，通常为 `SELECT`
    - `sources`: List[DqlSourceExpr] - 数据源列表
    - `columns`: List[DqlColumnExpr] - 列列表
    - `clause_select`: List[str] - SELECT子句内容
    - `clauses`: List[DqlClause] - 所有子句
    - `subquery`: Dict[str, ParsedQuery] - 子查询字典
  - UNION 形态：
    - `T`: str - 语句类型，通常为 `UNIONS`
    - `unions`: List[ParsedQuery | str] - UNION查询列表

**主要方法**:
- `format(indent, init_indent)`: 格式化查询
- `ast()`: 生成AST
- `tokens()`: 获取Tokens
- `available_cte()`: 获取当前查询作用域内可用的所有CTE。这些CTE通常来自于祖先ParsedQuery/ParsedInsert对象，包括当前查询和父级查询中定义的WITH子句。返回一个字典，键为CTE名称，值为ParsedCTE对象。
- `tokenize(statement, dialect=DialectType.ANSI)`: 静态方法，快速词法分析。`dialect` 为 `DialectType`（默认 `DialectType.ANSI`）。

**示例**:
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

# 提取信息
print("数据源:", parsed.sources)
print("列:", parsed.columns)
for i, clause in enumerate(parsed.clauses):
    if clause.part == "CLAUSE_FROM":
        print(f"FROM子句: {clause.clause}")
    elif clause.part == "CLAUSE_WHERE":
        print(f"WHERE条件: {clause.clause}")
    elif clause.part == "CLAUSE_AGGREGATION":
        print(f"GROUP BY: {clause.clause}")
    elif clause.part == "CLAUSE_SORT":
        print(f"ORDER BY: {clause.clause}")
    elif clause.part == "CLAUSE_LIMIT":
        print(f"LIMIT: {clause.clause}")

# 快速tokenizer
tokens = ParsedQuery.tokenize(sql)
for token_value, token_type, pos in tokens[:5]:
    print(f"{token_type}: {token_value}")
```

---

### 3. ParsedCTE - 公用表表达式解析器

**功能**: 解析WITH子句（CTE）

**参数**:
- `statement` (str): WITH语句
- `pure` (bool, default=False): 控制 SQL 注释处理。`True` 会在解析前移除 `--` 与 `/* ... */` 注释，因此格式化结果和 tokens 不含注释，且解析可能更快；`False` 保留注释。
- `dialect` (str, default=`"ansi"`): SQL 方言。支持：`ansi`、`mysql`、`postgresql`、`sqlite`、`doris`。可使用 `Dialects.<NAME>.value` 进行类型安全选择。

**主要属性**:
- `raw`: 原始CTE语句
- `units`: CTE语句列表
- `dialect`: 解析使用的方言

**主要方法**:
- `format(indent, init_indent)`: 格式化CTE
- `ast()`: 生成AST
- `tokenize(statement, dialect=DialectType.ANSI)`: 静态方法，快速词法分析。`dialect` 为 `DialectType`（默认 `DialectType.ANSI`）。

**示例**:
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
print("CTE语句:", cte.units)
print("格式化:\n", cte.format())

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
    print("CTEs对象:", query.cte)
    # common_tables 和 expressions 是 CommonTableExpr 对象的属性
    print("common tables:", query.cte.common_tables)
    print("expressions:", query.cte.expressions)
    for cte_name in query.cte.expressions:
        print("CTE名称:", cte_name)
        print("CTE语句:", query.cte.expressions[cte_name].format())
```

---

### 4. ParsedInsert - INSERT语句解析器

**功能**: 解析INSERT语句，支持VALUES和SELECT两种方式

**参数**:
- `statement` (str): INSERT语句
- `pure` (bool, default=False): 控制 SQL 注释处理。`True` 会在解析前移除 `--` 与 `/* ... */` 注释，因此格式化结果和 tokens 不含注释，且解析可能更快；`False` 保留注释。
- `dialect` (str, default=`"ansi"`): SQL 方言。支持：`ansi`、`mysql`、`postgresql`、`sqlite`、`doris`。可使用 `Dialects.<NAME>.value` 进行类型安全选择。

**主要属性**:
- `name`: str - 目标表名
- `columns`: List[str] - 插入的列列表
- `values`: List[str] - 插入的值
- `query`: ParsedQuery - 查询对象（INSERT...SELECT时）
- `query_load`: bool - 是否有查询加载
- `main_stmt`: str - 主语句
- `cte`: ParsedWithStmt - CTE解析对象（INSERT语句级别的CTE，定义在INSERT之前的WITH子句）。注意：此对象的属性与ParsedQuery.cte不同，主要通过 `.units` 访问CTE单元列表。
- `cte_stmt`: str - CTE语句
- `query_stmt`: str - 查询语句

**主要方法**:
- `format(indent, init_indent)`: 格式化
- `ast()`: 生成AST
- `tokens()`: 获取Tokens
- `tokenize(statement, dialect=DialectType.ANSI)`: 静态方法，快速词法分析。`dialect` 为 `DialectType`（默认 `DialectType.ANSI`）。

**示例**:
```python
from fastsqlparse import ParsedInsert, ParsedQuery

sql1 = "INSERT INTO users (id, name) VALUE (1, 'Alice')"
insert1 = ParsedInsert(sql1)
print("表名:", insert1.name)
print("列:", insert1.columns)
print("值:", insert1.values)

# SELECT方式（带CTE）
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
print("表名:", insert2.name)
print("有查询:", insert2.query_load)
# 注意：insert2.cte 是 ParsedWithStmt 类型，与 query.cte (CommonTableExpr) 不同
if insert2.cte:
    print("INSERT级别的CTE单元:", insert2.cte.units)
if insert2.query:
    print("查询对象类型:", type(insert2.query))
    parsed_query: ParsedQuery = insert2.query
    print("parsed_query.parsed:", parsed_query.parsed)
    # parsed_query.cte 是 CommonTableExpr 类型，有 common_tables 和 expressions 属性
    print("parsed_query.cte:", parsed_query.cte)
    if parsed_query.cte:
        # common_tables 和 expressions 是 CommonTableExpr 对象的属性
        print("common_tables:", parsed_query.cte.common_tables)
        print("expressions:", parsed_query.cte.expressions)
```

---

### 5. 其他解析器类

以下类的构造函数均接受 `pure`（bool，默认 `False`）与 `dialect`（str，默认 `"ansi"`），并提供 `tokenize(statement, dialect=DialectType.ANSI)` 类方法用于快速词法分析。

#### ParsedView - VIEW解析器
```python
from fastsqlparse import ParsedView

sql = "CREATE VIEW active_users AS SELECT * FROM users WHERE status='active'"
view = ParsedView(sql, pure=False, dialect="mysql")
```

#### ParsedUpdate - UPDATE解析器
```python
from fastsqlparse import ParsedUpdate

sql = "UPDATE users SET status='inactive' WHERE last_login < '2023-01-01'"
update = ParsedUpdate(sql, pure=False, dialect="mysql")
```

#### ParsedDelete - DELETE解析器
```python
from fastsqlparse import ParsedDelete

sql = "DELETE FROM logs WHERE created_at < '2023-01-01'"
delete = ParsedDelete(sql, pure=False, dialect="mysql")
```

#### ParsedCreate - CREATE TABLE解析器
```python
from fastsqlparse import ParsedCreate

sql = """
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(200)
)
"""
create = ParsedCreate(sql, pure=False, dialect="mysql")

# 提取 CREATE 语句的词法 tokens
toks = create.tokens()
# 直接对 CREATE 语句字符串进行快速词法分析
toks = ParsedCreate.tokenize(sql, dialect=DialectType.MYSQL)
```

> 说明：`ParsedCreate.tokens()` 提取已解析 CREATE 语句的词法 tokens；`ParsedCreate.tokenize(statement, dialect)` 对 CREATE 语句字符串进行轻量词法分析。

---

## 功能演示

### 场景1: 普通查询（含子查询）

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

# 提取关键信息
print("parsed:", parsed)
print("数据源:", parsed.sources)
print("列:", parsed.columns)
print("SELECT子句:", parsed.clause_select)
print("子查询:", parsed.subquery)
for clause in parsed.clauses:
    if clause.part == "CLAUSE_FROM":
        print(f"FROM子句: {clause.clause}")
    elif clause.part == "CLAUSE_WHERE":
        print(f"WHERE子句: {clause.clause}")
    elif clause.part == "CLAUSE_SORT":
        print(f"ORDER BY子句: {clause.clause}")
    elif clause.part == "CLAUSE_LIMIT":
        print(f"LIMIT子句: {clause.clause}")
```

**输出**:
```
parsed: QueryStatement(type=SELECT)

数据源: [DqlSourceExpr(table='users', alias='u')]
列: [DqlColumnExpr(name='user_id', table='u'), DqlColumnExpr(name='username', table='u'), ...]
SELECT子句: ['u.user_id', 'u.username', '(SELECT COUNT(*) ...) as order_count']
子查询: {'order_count': ParsedQuery(position=45, name='order_count' at 0x...)}
FROM子句: FROM users u
WHERE子句: WHERE u.age > 18
ORDER BY子句: ORDER BY u.username
LIMIT子句: LIMIT 10
```

---

### 场景2: 临时结果集（聚合查询）

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
    # common_tables 和 expressions 是 CommonTableExpr 对象的属性
    if query.cte:
        print(f"common tables: {query.cte.common_tables}")
        print(f"expressions: {query.cte.expressions}")

print(f"TOKENS数量: {len(parsed.tokens())}")
print(f"前5个TOKENS:")
for i, token in enumerate(parsed.tokens()[:5]):
    print(token)

# 获取AST
ast_str = parsed.AST()
ast_obj = json.loads(ast_str)
print(json.dumps(ast_obj, indent=2, ensure_ascii=False)[:500] + "...")
```

---

### 场景3: UNION查询 + Tokenizer

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

# 使用Tokenizer进行快速词法分析
tokens = ParsedQuery.tokenize(sql)
print(f"Tokenizer结果 (前10个token):")
for i, (token_value, token_type, position) in enumerate(tokens[:10]):
    print(f"  {i}: type={token_type}, value='{token_value}', pos={position}")
```

---

### 场景4: INSERT INTO ... CTE SELECT

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

print("目标表名:", insert_parsed.name)
print("插入的列:", insert_parsed.columns)
print("是否有查询加载:", insert_parsed.query_load)
# 注意：insert_parsed.cte 是 ParsedWithStmt 类型
if insert_parsed.cte:
    print("INSERT级别的CTE单元:", insert_parsed.cte.units)
if insert_parsed.query:
    print("查询对象类型:", type(insert_parsed.query))
    print("查询的sources:", insert_parsed.query.parsed.sources)
print("insert_parsed.cte:", insert_parsed.cte)

parsed_query: ParsedQuery = insert_parsed.query
print("parsed_query:", parsed_query)
print("parsed_query.parsed:", parsed_query.parsed)
# parsed_query.cte 是 CommonTableExpr 类型，有 common_tables 和 expressions 属性
print("parsed_query.cte:", parsed_query.cte)
if parsed_query.cte:
    # common_tables 和 expressions 是 CommonTableExpr 对象的属性
    print("parsed_query.cte.common_tables:", parsed_query.cte.common_tables)
    print("parsed_query.cte.expressions:", parsed_query.cte.expressions)
print("parsed_query.parsed.columns:", parsed_query.parsed.columns)
```

---

### 场景5: 处理注释和格式化

```python
from fastsqlparse import Parsed, strip_comments

sql = """
-- 这是用户查询的主注释
SELECT 
    u.user_id,  -- 用户ID
    u.username  -- 用户名
FROM users u  /* 用户表 */
WHERE u.status = 'active'  -- 只查活跃用户
"""

# 保留注释并格式化
parsed_with_comments = Parsed(sql, pure=False)
print("保留注释的格式化结果:")
print(parsed_with_comments.format())

# 去掉注释并格式化
parsed_pure = Parsed(sql, pure=True)
print("\n去掉注释的格式化结果:")
print(parsed_pure.format())

# 仅去除注释（不格式化）
stripped = strip_comments(sql)
print("\n仅去除注释:")
print(stripped)
```

---

## 性能对比

### 测试环境
- SQL长度: 1359字符
- 测试次数: 100次

结果（`test/test_fastsqlparse.py`，100 次）：

| 解析器 | 总耗时 | 平均每次 | 加速比 |
|--------|--------|----------|--------|
| **fastsqlparse** | 0.0151s | 0.15ms | - |
| sqlglot | 0.2811s | 2.81ms | 18.62x |
| sqlparse | 0.8735s | 8.73ms | 57.86x |

### 大规模测试

#### 测试1: 5000次解析
- SQL长度: 639字符
- 总耗时: 0.4832秒
- **PPS (Parses Per Second): 10347.38**
- 平均每次: 0.0966ms

#### 测试2: 1000万字符SQL
- SQL长度: 10,500,998字符
- 总耗时: 0.5393秒
- **CPS (Characters Per Second): 19,472,920.75**
- 解析成功！

#### 测试3: 仅 Python 四库对比（约 10M PostgreSQL SQL，不含 C 版本）

基准脚本：`test/python_parsers_10m.py`

| 解析器 | 平均耗时 | CPS |
|--------|----------|-----|
| **fastsqlparse** | 0.7394s | 13,524,892.44 |
| pglast | 4.8541s | 2,060,217.57 |
| sqlglot (postgres) | 20.5364s | 486,963.12 |
| sqlparse | 84.9591s | 117,709.35 |

说明：
- SQL长度：10,000,484字符
- 每个解析器运行次数：1
- 结果来源：`test/benchmark_results/python_parsers_10m.json`运行结果

---

## API参考

### 方言（Dialects）

解析器通过 `dialect` 参数（默认 `"ansi"`）支持多种 SQL 方言。所有解析器构造函数（`Parsed`、`ParsedOne`、`ParsedQuery`、`ParsedInsert`、`ParsedCTE`、`ParsedUpdate`、`ParsedDelete`、`ParsedView`、`ParsedCreate`）均接受字符串形式的 `dialect`；`tokenize(...)` 类方法与 `ParsedQuery.parse_dependence(...)` 接受 `DialectType` 类型的 `dialect`（默认 `DialectType.ANSI`）。

支持的方言（通过 `Dialects` 枚举暴露，并由 `fastsqlparse` 重新导出）：

| `Dialects` 成员 | `.value` | `DialectType` 常量 |
|-------------------|----------|------------------------|
| `Dialects.ANSI` | `"ansi"` | `DIALECT_ANSI` |
| `Dialects.MYSQL` | `"mysql"` | `DIALECT_MYSQL` |
| `Dialects.POSTGRESQL` | `"postgresql"` | `DIALECT_POSTGRESQL` |
| `Dialects.SQLITE` | `"sqlite"` | `DIALECT_SQLITE` |
| `Dialects.DORIS` | `"doris"` | `DIALECT_DORIS` |

`DialectType` 是 `pysqlparser.DIALECT` 的别名，用于需要类型化方言选择器的场合（如 `tokenize`）。`Dialects.<NAME>.value` 返回构造函数接受的字符串形式。

```python
from fastsqlparse import Parsed, ParsedQuery, Dialects, DialectType

# 构造函数使用字符串方言
parsed = Parsed(sql, dialect=Dialects.MYSQL.value)          # "mysql"
query = ParsedQuery(sql, "q", dialect="postgresql")

# tokenize / parse_dependence 使用 DialectType
ParsedQuery.tokenize(sql, dialect=DialectType.MYSQL)
ParsedQuery.parse_dependence(sql, dialect="mysql")
```

### 工具函数

#### `strip_comments(sql: str) -> str`
去除 SQL 注释

```python
from fastsqlparse import strip_comments

sql = "SELECT * FROM users -- comment"
clean = strip_comments(sql)
# 结果: "SELECT * FROM users"
```


#### `format(sql: str, indent: str = "    ") -> str`
格式化SQL语句

```python
from fastsqlparse import format

sql = "SELECT * FROM users WHERE id=1"
formatted = format(sql, indent="  ")
```
#### `tokenize(sql: str, dialect: DialectType = DialectType.ANSI) -> List[Tuple[str, str, int]]`
词法分析

返回的元组顺序为 `(token_value, token_type, position)`。

#### `tokenize_query(sql: str, dialect: DialectType = DialectType.ANSI) -> List[Tuple[str, str, int]]`
快速词法分析SELECT语句

```python
from fastsqlparse import tokenize_query, DialectType

tokens = tokenize_query("SELECT * FROM users", dialect=DialectType.MYSQL)
```

#### `tokenize_cte(sql: str, dialect: DialectType = DialectType.ANSI) -> List[Tuple[str, str, int]]`
快速词法分析WITH语句

#### `tokenize_insert(sql: str, dialect: DialectType = DialectType.ANSI) -> List[Tuple[str, str, int]]`
快速词法分析INSERT语句

#### `tokenize_update(sql: str, dialect: DialectType = DialectType.ANSI) -> List[Tuple[str, str, int]]`
快速词法分析UPDATE语句

#### `tokenize_delete(sql: str, dialect: DialectType = DialectType.ANSI) -> List[Tuple[str, str, int]]`
快速词法分析DELETE语句

#### `tokenize_view(sql: str, dialect: DialectType = DialectType.ANSI) -> List[Tuple[str, str, int]]`
快速词法分析VIEW语句

---

### Token结构

每个Token包含以下属性:
- `type`: Token类型（KEYWORD, IDENTIFIER, NUMBER/STRING, WHITESPACE等）
- `value`: Token的值
- `position`: 在SQL中的位置

```python
tokens = parsed.tokens()
for token in tokens:
    print(f"Type: {token.type}, Value: {token.value}, Pos: {token.at}")
```

**Token类型**:
- `KEYWORD`: SQL关键字 (SELECT, FROM, WHERE等)
- `IDENTIFIER`: 标识符 (表名、列名、别名)
- `NUMBER/STRING`: 字面量 (数字、字符串)
- `WHITESPACE`: 空白字符
- `SUBQUERY`: 子查询
- `OPERATOR`: 运算符
- `COMMENT`: 注释

---

### 常见 AST / 类型速查

以下类型会在解析结果和示例中反复出现：

| 类型 | 常见字段 | 说明 |
|------|----------|------|
| `DqlSourceExpr` | `table`, `alias` | FROM/JOIN 数据源表达式 |
| `DqlColumnExpr` | `name`, `table`, `alias` | SELECT / 派生列元数据 |
| `DqlClause` | `part`, `clause` | 单个查询子句节点 |
| `QueryStatement` | `T`, `sources`, `columns`, `clauses`, `subquery`, `clause_select` 或 `T`, `unions` | SELECT / UNION 解析结构 |
| `CommonTableExpr` | `common_tables`, `expressions` | SELECT 级别 CTE 容器 |
| `ParsedWithStmt` | `units` | INSERT 级别 WITH 语句容器 |

---

### AST结构

AST以JSON格式返回，包含:
- 查询子句（SELECT, FROM, WHERE等）
- CTE定义
- 列信息
- 数据源信息
- 联合查询信息

```python
import json
ast_json_list = parsed.AST()
ast_json_dic = parsed_query.ast()
ast_obj = json.loads(ast_json_dic)
```

简单 SQL 的完整 AST 示例：

```python
import json
from fastsqlparse import Parsed

parsed = Parsed("SELECT a FROM t")
full_ast = json.loads(parsed.AST())
print(json.dumps(full_ast, indent=2, ensure_ascii=False))
```

---

## 最佳实践

### 1. 选择合适的解析器

- **通用SQL或多语句**: 使用 `Parsed`
- **单语句自动识别**: 使用 `ParsedOne` (推荐)
- **已知SELECT**: 使用 `ParsedQuery`
- **已知INSERT**: 使用 `ParsedInsert`
- **仅CTE**: 使用 `ParsedCTE`

### 2. 性能优化

- 如果只需要词法信息，使用 `tokenize()` 静态方法
- 设置 `pure=True` 会在解析前移除 `--` 和 `/* ... */` 注释；通常可提升速度，并让格式化结果与 tokens 不含注释
- 避免重复解析相同SQL，缓存解析结果

### 3. 错误处理

底层解析失败会以标准 Python 异常的形式抛出，大多数场景直接使用 `except Exception as e` 即可。

```python
from fastsqlparse import Parsed

try:
    parsed = Parsed(invalid_sql)
except Exception as e:
    print(f"解析失败: {e}")
```

---

## 常见问题

### Q1: 如何提取表名？
```python
from fastsqlparse import ParsedOne, ParsedQuery

parsed = ParsedOne(sql)
if parsed.type == "query":
    query: ParsedQuery = parsed.parsed
    for source in query.parsed.sources:
        print(source.table)  # 或查看source的属性
```

### Q2: 如何处理多语句SQL？
```python
from fastsqlparse import Parsed

parsed = Parsed("SELECT * FROM t1; SELECT * FROM t2;")
for stmt in parsed.parsed_forest:
    print(stmt)
```

### Q3: 如何获取子查询信息？
```python
from fastsqlparse import ParsedOne, ParsedQuery

parsed = ParsedOne(sql)
if parsed.type == "query":
    query: ParsedQuery = parsed.parsed
    if query.parsed.subquery:
        for subq_name, subq in query.parsed.subquery.items():
            print(f"子查询名称: {subq_name}")
            print(f"子查询对象: {subq}")
```

### Q4: 如何使用available_cte()获取可用的CTE？
```python
from fastsqlparse import ParsedQuery

sql = """
WITH cte1 AS (SELECT 1 as n)
SELECT * FROM cte1
"""

query = ParsedQuery(sql, 'test')
available_ctes = query.available_cte()
print("可用的CTE:", available_ctes)
```

---

## GitHub仓库

https://github.com/Nohaltsail/fast-pysqlparse

## 许可证

本项目采用 **MIT 许可证** - 详情请参见 [LICENSE](LICENSE) 文件。

### 关于动态库的说明

本项目当前分发预编译动态库（`.pyd` 和 `.so`）。
这些动态库对应的 C++ 源代码目前暂未公开，计划在后续版本开放。
