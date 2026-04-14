# fast-sqlparse API 文档与使用指南

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

```python
import fastsqlparse
from fastsqlparse import ParsedSQL, ParsedQuery, ParsedCTE, ParsedInsert

# 解析SQL
sql = "SELECT * FROM users WHERE age > 18"
parsed = ParsedSQL(sql)

# 获取解析结果
query = parsed.parseforest[0]
print(query.sources)    # 数据源
print(query.columns)    # 列信息
print(query.format())   # 格式化输出
```

---

## 核心类说明

### 1. ParsedSQL - SQL解析器主类

**功能**: 解析任意SQL语句（SELECT、INSERT、UPDATE、DELETE、CREATE等）

**参数**:
- `sql_statements` (str): SQL语句字符串
- `file` (str, optional): SQL文件路径
- `name` (str, optional): 解析内容名称
- `pure` (bool, default=False): 是否忽略注释

**主要属性和方法**:
- `parseforest`: 返回解析后的语句列表
- `statements`: 所有SQL语句
- `tokens()`: 获取词法单元
- `AST()`: 获取抽象语法树（JSON格式）
- `format(indent)`: 格式化SQL
- `content()`: 获取原始SQL内容
- `name`: SQL语句名称

**示例**:
```python
sql = "SELECT u.id, u.name FROM users u WHERE u.age > 18"
parsed = ParsedSQL(sql)

# 获取解析树
items = parsed.parseforest

# 格式化
formatted = parsed.format(indent="  ")

# 获取AST
ast_json = parsed.AST()

# 获取Tokens
tokens = parsed.tokens()
```

---

### 2. ParsedQuery - SELECT查询解析器

**功能**: 专门解析SELECT查询语句，提取查询子句和元数据

**参数**:
- `statement` (str): SELECT语句
- `name` (str): 查询名称
- `pure` (bool, default=False): 是否去除注释

**主要属性**:
- `sources`: 数据源列表（FROM/JOIN的表）
- `columns`: 选择的列列表
- `clause_select`: SELECT子句内容
- `clause_from`: FROM子句内容
- `clause_condition`: WHERE子句内容
- `clause_aggregation`: GROUP BY/HAVING子句
- `clause_sorting`: ORDER BY子句
- `clause_limit`: LIMIT子句
- `cte_names`: CTE名称列表
- `cte`: CTE映射字典
- `unions`: UNION查询列表
- `subquery`: 子查询信息
- `level`: 嵌套层级

**主要方法**:
- `format(indent, init_indent)`: 格式化查询
- `ast()`: 生成AST
- `tokens()`: 获取Tokens
- `tokenize(statement)`: 静态方法，快速词法分析

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

# 提取信息
print("数据源:", query.sources)
print("列:", query.columns)
print("WHERE条件:", query.clause_condition)
print("GROUP BY:", query.clause_aggregation)
print("ORDER BY:", query.clause_sorting)

# 快速tokenizer
tokens = ParsedQuery.tokenize(sql)
for token_type, token_value, pos in tokens[:5]:
    print(f"{token_type}: {token_value}")
```

---

### 3. ParsedCTE - 公用表表达式解析器

**功能**: 解析WITH子句（CTE）

**参数**:
- `statement` (str): WITH语句
- `pure` (bool, default=False): 是否去除注释
- `name` (str, optional): CTE名称

**主要属性**:
- `raw`: 原始CTE语句
- `cte_stmts`: CTE语句列表
- `name`: CTE名称

**主要方法**:
- `format(indent, init_indent)`: 格式化CTE
- `ast()`: 生成AST
- `tokenize(statement)`: 静态方法，快速词法分析

**示例**:
```python
from fastsqlparse import ParsedCTE

sql = """
WITH RECURSIVE cte AS (
    SELECT 1 as n
    UNION ALL
    SELECT n + 1 FROM cte WHERE n < 10
)
SELECT * FROM cte
"""

cte = ParsedCTE(sql)
print("CTE语句:", cte.cte_stmts)
print("格式化:\n", cte.format())

# Tokenizer
tokens = ParsedCTE.tokenize(sql)
```

---

### 4. ParsedInsert - INSERT语句解析器

**功能**: 解析INSERT语句，支持VALUES和SELECT两种方式

**参数**:
- `statement` (str): INSERT语句
- `pure` (bool, default=False): 是否去除注释

**主要属性**:
- `name`: 目标表名
- `columns`: 插入的列列表
- `values`: 插入的值
- `query`: 查询对象（INSERT...SELECT时）
- `query_load`: 是否有查询加载
- `main_stmt`: 主语句
- `cte_stmt`: CTE语句
- `query_stmt`: 查询语句

**主要方法**:
- `format(indent, init_indent)`: 格式化
- `ast()`: 生成AST
- `tokens()`: 获取Tokens
- `tokenize(statement)`: 静态方法，快速词法分析

**示例**:
```python
from fastsqlparse import ParsedInsert

# VALUES方式
sql1 = "INSERT INTO users (id, name) VALUES (1, 'Alice')"
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
SELECT product_id, total FROM stats
"""
insert2 = ParsedInsert(sql2)
print("表名:", insert2.name)
print("有查询:", insert2.query_load)
if insert2.query:
    print("查询来源:", insert2.query.sources)
```

---

### 5. 其他解析器类

#### ParsedView - VIEW解析器
```python
from fastsqlparse import ParsedView

sql = "CREATE VIEW active_users AS SELECT * FROM users WHERE status='active'"
view = ParsedView(sql)
```

#### ParsedUpdate - UPDATE解析器
```python
from fastsqlparse import ParsedUpdate

sql = "UPDATE users SET status='inactive' WHERE last_login < '2023-01-01'"
update = ParsedUpdate(sql)
```

#### ParsedDelete - DELETE解析器
```python
from fastsqlparse import ParsedDelete

sql = "DELETE FROM logs WHERE created_at < '2023-01-01'"
delete = ParsedDelete(sql)
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
create = ParsedCreate(sql)
```

---

## 功能演示

### 场景1: 普通查询（含子查询）

```python
from fastsqlparse import ParsedSQL

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

parsed = ParsedSQL(sql)
query = parsed.parseforest[0]

# 提取关键信息
print("数据源:", query.sources)
print("列:", query.columns)
print("SELECT:", query.clause_select)
print("FROM:", query.clause_from)
print("WHERE:", query.clause_condition)
print("ORDER BY:", query.clause_sorting)
print("LIMIT:", query.clause_limit)
```

**输出**:
```
数据源: [<DqlSourceExpr object>]
列: [<DqlColumnExpr object>, ...]
SELECT: ['u.user_id', 'u.username', '(SELECT COUNT(*) ...) as order_count']
FROM: FROM users u
WHERE: WHERE u.age > 18
ORDER BY: ORDER BY u.username
LIMIT: LIMIT 10
```

---

### 场景2: 临时结果集（聚合查询）

```python
from fastsqlparse import ParsedSQL
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

parsed = ParsedSQL(sql)

# 获取Tokens
tokens = parsed.tokens()
print(f"Token数量: {len(tokens)}")

# 获取AST
ast_str = parsed.AST()
ast_obj = json.loads(ast_str)
print(json.dumps(ast_obj, indent=2, ensure_ascii=False))
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
for token_type, token_value, position in tokens:
    print(f"Type: {token_type:15} | Value: {token_value[:30]:30} | Pos: {position}")
```

---

### 场景4: INSERT INTO ... CTE SELECT

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

print("目标表:", insert.name)
print("插入列:", insert.columns)
print("有查询:", insert.query_load)

if insert.query:
    print("查询类型:", type(insert.query))
    print("查询来源:", insert.query.sources)
    print("查询列:", insert.query.columns)
```

---

### 场景5: 处理注释和格式化

```python
from fastsqlparse import ParsedSQL, strip_note

sql = """
-- 这是主注释
SELECT 
    u.user_id,  -- 用户ID
    u.username  -- 用户名
FROM users u  /* 用户表 */
WHERE u.status = 'active'  -- 只查活跃用户
"""

# 保留注释并格式化
parsed_with_comments = ParsedSQL(sql, pure=False)
print("保留注释:")
print(parsed_with_comments.format())

# 去除注释并格式化
parsed_pure = ParsedSQL(sql, pure=True)
print("\n去除注释:")
print(parsed_pure.format())

# 仅去除注释（不格式化）
stripped = strip_note(sql)
print("\n仅去注释:")
print(stripped)
```

---

## 性能对比

### 测试环境
- SQL长度: ~1250字符
- 测试次数: 100次

### 性能结果

| 解析器 | 总耗时(100次) | 平均每次 | 相对速度 |
|--------|--------------|---------|---------|
| **fast-sqlparse** | 0.119秒 | 1.19ms | **1.0x** (基准) |
| sqlparse | 1.216秒 | 12.16ms | 10.23x 慢 |
| sqlglot | 0.322秒 | 3.22ms | 2.71x |

### 大规模测试

#### 测试1: 5000次解析
- SQL长度: 639字符
- 总耗时: 3.96秒
- **PPS (Parses Per Second): 1262**
- 平均每次: 0.79ms

#### 测试2: 1000万字符SQL
- SQL长度: 10,500,998字符
- 总耗时: 13.06秒
- **CPS (Characters Per Second): 803,774**

---

## API参考

### 工具函数

#### `strip_note(sql: str) -> str`
去除SQL中的注释

```python
from fastsqlparse import strip_note

sql = "SELECT * FROM users -- comment"
clean = strip_note(sql)
# 结果: "SELECT * FROM users"
```

#### `format(sql: str, indent: str = "    ") -> str`
格式化SQL语句

```python
from fastsqlparse import format

sql = "SELECT * FROM users WHERE id=1"
formatted = format(sql, indent="  ")
```
#### `tokenize(sql: str) -> List[Tuple[str, str, int]]`
词法分析

#### `tokenize_query(sql: str) -> List[Tuple[str, str, int]]`
快速词法分析SELECT语句

```python
from fastsqlparse import tokenize_query

tokens = tokenize_query("SELECT * FROM users")
```

#### `tokenize_cte(sql: str) -> List[Tuple[str, str, int]]`
快速词法分析WITH语句

#### `tokenize_insert(sql: str) -> List[Tuple[str, str, int]]`
快速词法分析INSERT语句

#### `tokenize_update(sql: str) -> List[Tuple[str, str, int]]`
快速词法分析UPDATE语句

#### `tokenize_delete(sql: str) -> List[Tuple[str, str, int]]`
快速词法分析DELETE语句

#### `tokenize_view(sql: str) -> List[Tuple[str, str, int]]`
快速词法分析VIEW语句

---

### Token结构

每个Token包含以下属性:
- `type`: Token类型（KEYWORD, IDENTIFIER, LITERAL, WHITESPACE等）
- `value`: Token的值
- `position`: 在SQL中的位置

```python
tokens = parsed.tokens()
for token in tokens:
    print(f"Type: {token.type}, Value: {token.value}, Pos: {token.position}")
```

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
ast_json = parsed.AST()
ast_obj = json.loads(ast_json)
```

---

## 最佳实践

### 1. 选择合适的解析器

- **通用SQL**: 使用 `ParsedSQL`
- **仅SELECT**: 使用 `ParsedQuery`（更快）
- **仅INSERT**: 使用 `ParsedInsert`
- **仅CTE**: 使用 `ParsedCTE`

### 2. 性能优化

- 如果只需要词法信息，使用 `tokenize()` 静态方法
- 设置 `pure=True` 可以跳过注释处理，提升速度
- 避免重复解析相同SQL，缓存解析结果

### 3. 错误处理

```python
from fastsqlparse import ParsedSQL

try:
    parsed = ParsedSQL(invalid_sql)
except Exception as e:
    print(f"解析失败: {e}")
```

---

## 常见问题

### Q1: 如何提取表名？
```python
query = parsed.parseforest[0]
for source in query.sources:
    print(source.table_name)  # 或查看source的属性
```

### Q2: 如何处理多语句SQL？
```python
parsed = ParsedSQL("SELECT * FROM t1; SELECT * FROM t2;")
for stmt in parsed.parseforest:
    print(stmt)
```

### Q3: 如何获取子查询信息？
```python
query = parsed.parseforest[0]
if query.subquery:
    for subq in query.subquery:
        print(subq)
```

---

## GitHub仓库

https://github.com/Nohaltsail/fast-pysqlparse

## 许可证

Apache-2.0
