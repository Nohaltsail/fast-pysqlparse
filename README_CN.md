# fast-pysqlparse - 高性能SQL解析库

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Version](https://img.shields.io/badge/version-0.8-blue)]()
[![Language](https://img.shields.io/badge/language-Python%20%7C%20C++17-blue)]()
[![License](https://img.shields.io/badge/license-MIT-purple)]()

一个以 **快** 为核心特点的高性能、跨平台、轻量级 SQL 解析库，基于 C++17 核心引擎与原生 Python 绑定，对结构与层级特别复杂的 SQL 语句进行快速结构化解析。

---

## 目录

- [项目概述](#项目概述)
- [核心特性](#核心特性)
- [性能基准](#性能基准)
- [架构设计](#架构设计)
- [支持的SQL特性](#支持的sql特性)
- [快速开始](#快速开始)
- [使用场景](#使用场景)
- [API参考](#api参考)
- [安装指南](#安装指南)

---

## 项目概述

fast-pysqlparse 旨在解决传统 Python SQL 解析器在性能与功能上的局限。通过将计算密集的解析工作下沉到原生 C++ 层，对大型、深度嵌套、结构复杂的 SQL 仍保持极速解析。

解析器主要针对 ANSI 风格 SQL 进行解析。对于明确方言的SQL语句，推荐指定方言进行解析，支持指定：MySQL、POSTGRESQL、SQLite、Doris

### 设计理念

- **极致性能**: C++17 核心引擎，解析速度远超纯 Python 方案（详见性能基准）
- **结构化解析**: 面向复杂结构与深层级 SQL，尤其是CTE与SELECT、INSERT、VIEW等混用语句
- **深度解析**: 完整的 AST 生成、词法分析、表血缘追踪能力
- **易于使用**: 简洁直观的 Python API，开箱即用
- **跨平台**: Windows (.pyd) 和 Linux (.so) 原生扩展支持

---

## 最新更新 (v0.8)

### 性能突破

**超高速解析能力** 
- **对比sqlparse**: 快 **~115x**
- **对比sqlglot**: 快 **~28x**
- **对比pglast(底层为C编译的动态库)**: 快 **~6.5x**
- **吞吐量**: ~10300 PPS (Parses Per Second)
- **大文件处理**: 1000万字符SQL仅需约0.5秒 (~19,500,000 CPS)

### 新增核心功能

**方言（dialect）支持** 
- 新增 `Dialects` 枚举与 `DialectType`，支持 `ansi`/`mysql`/`postgresql`/`sqlite`/`doris`
- 所有解析器构造函数、`tokenize`、`parse_dependence` 均可指定 `dialect`（默认 `ansi`）

**性能优化** 
- 核心解析路径进一步提速，大文件 CPS 与 PPS 显著提升

**ParsedCreate 增强** 
- 新增 `tokens()` 实例方法与 `tokenize()` 类方法，支持 CREATE 语句的词法分析

### 既有能力

**增强的CTE支持** 
- 支持嵌套CTE定义
- 递归CTE解析
- CTE与INSERT/SELECT/UNION的组合使用
- CTE血缘关系提取
- 大量复杂嵌套子查询

**智能注释处理** 
- `pure=True` 模式：在解析前移除 `--` 与 `/* ... */` 注释，通常可提升解析速度，且格式化结果与 tokens 不含注释
- `pure=False` 模式：保留注释（默认）
- `strip_comments()` 工具函数：仅去除注释不格式化

**Tokenizer优化** 
- 静态方法快速词法分析：`ParsedQuery.tokenize(sql)`
- Token类型丰富：KEYWORD、IDENTIFIER、NUMBER/STRING、WHITESPACE、SUBQUERY等
- 位置信息完整：每个Token包含value、type、position

**INSERT语句增强** 
- 支持VALUES方式插入
- 支持SELECT方式插入（含CTE）
- 自动识别query_load状态
- 提取目标表名和插入列

**格式化引擎升级** 
- 智能缩进：根据子句层级自动调整
- 关键字大写：SELECT、FROM、WHERE等关键字统一格式化
- 注释对齐：保留或去除注释均可保持代码整洁

---

## 核心特性

### 双模式解析

**通用解析模式** (适合未知SQL类型):
```python
from fastsqlparse import Parsed

sql = "SELECT * FROM users WHERE age > 18"
parsed = Parsed(sql)
query = parsed.parsed_forest[0]
```

**专用解析模式** (已知SQL类型):
```python
from fastsqlparse import ParsedQuery, ParsedInsert

# SELECT专用
query = ParsedQuery("SELECT * FROM users", "simple-query")

# INSERT专用
insert = ParsedInsert("INSERT INTO users VALUES (1, 'Alice')")
```

### 完整的SQL支持

| 特性类别 | 支持内容 | 说明 |
|---------|---------|------|
| **查询语句** | SELECT、WITH、UNION、子查询 | 完整DQL支持 |
| **数据修改** | INSERT、UPDATE、DELETE | 完整DML支持 |
| **数据定义** | CREATE TABLE、CREATE VIEW | DDL基础支持 |
| **CTE** | WITH、WITH RECURSIVE、嵌套CTE | 公用表表达式 |
| **JOIN** | INNER JOIN、LEFT JOIN、RIGHT JOIN、FULL JOIN | 多表关联 |
| **聚合** | GROUP BY、HAVING、聚合函数 | 分组聚合 |
| **排序分页** | ORDER BY、LIMIT/OFFSET | 结果集控制 |
| **子查询** | 标量子查询、派生表、EXISTS | 嵌套查询 |
| **集合运算** | UNION、UNION ALL、INTERSECT、EXCEPT | 集合操作 |
| **注释处理** | `--`单行注释、`/* */`多行注释 | 灵活处理 |

### 解析能力

| 功能模块 | 能力描述                        | 输出形式 |
|---------|-----------------------------|---------|
| **AST生成** | 完整抽象结构树                     | JSON格式 |
| **Tokenization** | 词法分析                        | Token列表 (type, value, position) |
| **表血缘** | 源表到目标表追踪                    | 依赖关系图 |
| **列提取** | SELECT列、WHERE列、JOIN列        | ColumnExpr对象 |
| **数据源** | FROM/JOIN表、子查询              | SourceExpr对象 |
| **子句提取** | SELECT/FROM/WHERE/GROUP BY等 | Clause对象 |
| **格式化** | SQL美化输出                     | 格式化字符串 |
| **注释剥离** | 去除SQL注释                     | 纯净SQL |

---

## 性能基准

### 测试环境

- **测试SQL长度**: 1359字符（复杂多子查询+UNION）
- **迭代次数**: 100次
- **硬件**: 标准开发环境

### 大规模测试
`可以运行测试用例：test/test_fastsqlparse.py验证`
#### 测试1: 高并发解析 (5000次)
- **SQL长度**: 639字符
- **总耗时**: 0.4832秒
- **PPS**: **10347.38** Parses Per Second
- **平均延迟**: 0.0966ms/次

#### 测试2: 超大SQL解析 (1000万字符)
- **SQL长度**: 10,500,998字符
- **总耗时**: 0.5393秒
- **CPS**: **19,472,920.75** Characters Per Second
- **状态**: 解析成功

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
- 结果来源：result of `test/python_parsers_10m.py`

### 性能优势来源

1. **C++17核心引擎**: 编译型语言的原生性能
2. **string_view**：无拷贝字符串处理
3. **零拷贝设计**: Python与C++间最小化数据复制
4. **词法分析**: 手写有限状态机的
5. **优化的内存管理**: 减少GC压力
6. **并行友好**: 无全局锁，支持多线程解析

---

## 架构设计

fast-pysqlparse采用分层架构设计：

### 核心引擎层 (C++)

**位置**: `pysqlparser.cp*.pyd` / `pysqlparser.cpython-*.so`

**职责**:
- 词法分析 (Lexer)
- 语法分析 (Parser)
- AST构建


**技术栈**:
- C++17标准
- 手写递归下降解析器
- 优化的字符串处理
- 零拷贝内存管理

### Python绑定层

**位置**: `fastsqlparse/pysqlparser.pyi`

**职责**:
- 调用C++扩展
- 数据结构转换
- Pythonic API封装

**核心类**:
- `Parsed`: 通用SQL解析器, 解析多条SQL
- `ParsedOne`: 通用SQL解析器，解析单条或第一条有效SQL
- `ParsedQuery`: SELECT专用解析器
- `ParsedInsert`: INSERT专用解析器
- `ParsedCTE`: CTE专用解析器
- `ParsedUpdate`: UPDATE专用解析器
- `ParsedDelete`: DELETE专用解析器
- `ParsedCreate`: CREATE专用解析器
- `ParsedView`: VIEW专用解析器

### 业务逻辑层

**位置**: `fastsqlparse/statement/*.py`

**职责**:
- 高级查询分析
- 表血缘提取
- SQL格式化
- 工具函数

**模块**:
- `cte.py`: CTE处理逻辑
- `query.py`: 查询分析逻辑
- `insert.py`: INSERT分析逻辑
- `delete.py`: DELETE分析逻辑
- `update.py`: UPDATE分析逻辑
- `table_ddl.py`: DDL处理逻辑
- `view.py`: VIEW处理逻辑

### 数据流

```
SQL字符串
    ↓
[C++ Lexer] → Token序列
    ↓
[C++ Parser] → AST (内部表示)
    ↓
[Python Binding] → Python对象
    ↓
[Statement Layer] → 高级分析结果
    ↓
用户API (sources, columns, AST, format, etc.)
```

---

## 支持的SQL特性

### SELECT查询

**基础查询**:
```sql
SELECT user_id, username FROM users WHERE age > 18
```

**复杂JOIN**:
```sql
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id
LEFT JOIN payments p ON o.id = p.order_id
```

**子查询**:
```sql
SELECT u.*, 
    (SELECT COUNT(*) FROM orders WHERE user_id = u.id) as order_count
FROM users u
WHERE EXISTS (SELECT 1 FROM orders WHERE user_id = u.id)
```

**聚合查询**:
```sql
SELECT category, COUNT(*) as cnt, SUM(amount) as total
FROM products
GROUP BY category
HAVING cnt > 10
ORDER BY total DESC
LIMIT 10 OFFSET 20
```

### CTE (公用表表达式)

**基础CTE**:
```sql
WITH sales_summary AS (
    SELECT product_id, SUM(amount) as total
    FROM sales
    GROUP BY product_id
)
SELECT * FROM sales_summary WHERE total > 1000
```

**多CTE**:
```sql
WITH 
    cte1 AS (SELECT ...),
    cte2 AS (SELECT ... FROM cte1)
SELECT * FROM cte2
```

**递归CTE**:
```sql
WITH RECURSIVE hierarchy AS (
    SELECT id, parent_id, 0 as level
    FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.parent_id, h.level + 1
    FROM categories c JOIN hierarchy h ON c.parent_id = h.id
)
SELECT * FROM hierarchy
```

### INSERT语句

**VALUES方式**:
```sql
INSERT INTO users (id, name, age) VALUES (1, 'Alice', 30)
```

**SELECT方式**:
```sql
INSERT INTO summary (product_id, total)
SELECT product_id, SUM(amount)
FROM orders
GROUP BY product_id
```

**CTE + SELECT**:
```sql
INSERT INTO report (category, total_sales)
WITH stats AS (
    SELECT category, SUM(amount) as total
    FROM orders
    GROUP BY category
)
SELECT category, total FROM stats
```

### UPDATE & DELETE

**UPDATE**:
```sql
UPDATE users SET status = 'active' WHERE last_login > '2024-01-01'
```

**DELETE**:
```sql
DELETE FROM logs WHERE created_at < '2024-01-01'
```

### DDL

**CREATE TABLE**:
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(200)
)
```

**CREATE VIEW**:
```sql
CREATE VIEW active_users AS
SELECT * FROM users WHERE status = 'active'
```

---

## 快速开始

### 安装

```bash
pip install fast-pysqlparse
```

### 示例1: 基础查询解析

```python
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
print(f"parsed: {parsed}")
print(f"原始SQL:\n{query.raw}")
print(f"\n提取的sources: {parsed.sources}")
print(f"提取的columns: {parsed.columns}")
print(f"SELECT子句: {parsed.clause_select}")
print(f"子查询: {parsed.subquery}")
for i, clause in enumerate(parsed.clauses):
    if clause.part == "CLAUSE_FROM":
        print(f"FROM子句: {clause.clause}")
    elif clause.part == "CLAUSE_WHERE":
        print(f"WHERE子句: {clause.clause}")
    elif clause.part == "CLAUSE_SORT":
        print(f"ORDER子句: {clause.clause}")
    elif clause.part == "CLAUSE_LIMIT":
        print(f"LIMIT子句: {clause.clause}")
```

**输出**:
```
parsed: QueryStatement(type=SELECT)

提取的sources: [DqlSourceExpr(table='users', alias='u')]
提取的columns: [DqlColumnExpr(name='user_id', table='u'), DqlColumnExpr(name='username', table='u'), DqlColumnExpr(name='order_count', alias='order_count', table='@subquery')]
SELECT子句: ['u.user_id', 'u.username', '(SELECT COUNT(*) FROM orders o WHERE o.user_id = u.user_id) as order_count']
子查询: {'order_count': ParsedQuery(position=45, name='order_count' at 0x17148278D40)}
FROM子句: FROM users u

WHERE子句: WHERE u.age > 18

ORDER子句: ORDER BY u.username

LIMIT子句: LIMIT 10

```

### 示例2: CTE聚合查询

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

print(f"\nAST (JSON格式):")
ast_str = parsed.AST()
ast_obj = json.loads(ast_str)
print(json.dumps(ast_obj, indent=2, ensure_ascii=False)[:500] + "...")
# 格式化输出
print(parsed.format())
```

### 示例3: INSERT with CTE

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
print(f"目标表名: {insert_parsed.name}")
print(f"插入的列: {insert_parsed.columns}")
print(f"是否有查询加载: {insert_parsed.query_load}")
# 注意：insert_parsed.cte 是 ParsedWithStmt 类型
if insert_parsed.cte:
    print(f"INSERT级别的CTE单元: {insert_parsed.cte.units}")
if insert_parsed.query:
    print(f"查询对象类型: {type(insert_parsed.query)}")
    print(f"查询的sources: {insert_parsed.query.parsed.sources}")
print(f"insert_parsed.cte: {insert_parsed.cte}")

parsed_query: ParsedQuery = insert_parsed.query
print(f"parsed_query: {parsed_query}")
print(f"parsed_query.parsed: {parsed_query.parsed}")
# parsed_query.cte 是 CommonTableExpr 类型，有 common_tables 和 expressions 属性
print(f"parsed_query.cte: {parsed_query.cte}")
if parsed_query.cte:
    # common_tables 和 expressions 是 CommonTableExpr 对象的属性
    print(f"parsed_query.cte.common_tables: {parsed_query.cte.common_tables}")
    print(f"parsed_query.cte.expressions: {parsed_query.cte.expressions}")
print(f"parsed_query.parsed.columns: {parsed_query.parsed.columns}")
```

**输出**:
```
目标表名: summary_table
插入的列: ['product_id', 'total_amount', 'avg_amount']
是否有查询加载: True
查询对象类型: <class 'fastsqlparse.pysqlparser.Dql'>
insert_parsed.cte: None
parsed_query: ParsedQuery(position=66, name='query_load' at 0x1FB9ADE8BE0)
parsed_query.parsed: QueryStatement(type=SELECT)
parsed_query.cte: <fastsqlparse.pysqlparser.CommonTableExpr object at 0x000001FB9AB996B0>
parsed_query.cte.common_tables: ['product_stats']
parsed_query.cte.expressions: {'product_stats': ParsedCTE(position=66, name='product_stats' at 0x1FB9ADE7070)}
parsed_query.parsed.columns: [DqlColumnExpr(name='product_id'), DqlColumnExpr(name='total_amount'), DqlColumnExpr(name='avg_amount')]

```

### 示例4: 注释处理与格式化

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

### 示例5: Tokenizer快速词法分析

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

parsed_query = ParsedQuery(sql, "test_table")
parsed = parsed_query.parsed
print(f"query.parsed: {parsed}")
if parsed.T == "UNIONS":
    for e in parsed.unions:
        print(f"{e}")
```

**输出**:
```
Tokenizer结果 (前10个token):
  0: type=
, value='WHITESPACE', pos=0
  1: type=WITH, value='KEYWORD', pos=1
  2: type= , value='WHITESPACE', pos=5
  3: type=region_sales, value='IDENTIFIER', pos=6
  4: type= , value='WHITESPACE', pos=18
  5: type=AS, value='KEYWORD', pos=19
  6: type= , value='WHITESPACE', pos=21
  7: type=(
    SELECT region, SUM(amount) as total
    FROM sales
    GROUP BY region
), value='SUBQUERY', pos=22
  8: type=
, value='WHITESPACE', pos=100
  9: type=SELECT, value='KEYWORD', pos=101
query.parsed: QueryStatement(type=UNIONS, length=2)
ParsedQuery(position=101, name='test_table_0' at 0x2CD97659140)
UNION ALL
ParsedQuery(position=138, name='test_table_1' at 0x2CD9765AF60)

```

---

## 使用场景

### 场景选择指南

| **场景** | **推荐解析器**          | **原因** |
|---------|--------------------|---------|
| SQL类型未知 | `Parsed/ParsedOne` | 自动检测SQL类型 |
| 多语句脚本 | `Parsed`           | 支持分号分隔的多语句 |
| 纯SELECT查询 | `ParsedQuery`      | 性能最优，专用优化 |
| INSERT语句 | `ParsedInsert`     | 提取表名、列、查询 |
| UPDATE语句 | `ParsedUpdate`     | 提取更新字段、条件 |
| DELETE语句 | `ParsedDelete`     | 提取删除条件 |
| CREATE TABLE | `ParsedCreate`     | 提取表结构 |
| CREATE VIEW | `ParsedView`       | 提取视图定义 |
| CTE分析 | `ParsedCTE`        | 专门处理WITH子句 |

> **注意**: 如果SQL包含多个用分号分隔的语句（如脚本），**必须**使用`Parsed`。专用解析器仅适用于单个已知类型的语句。

### 典型应用场景

#### 1. SQL血缘分析
```python
from fastsqlparse import Parsed

sql = """
INSERT INTO summary
WITH stats AS (
    SELECT user_id, COUNT(*) as cnt
    FROM orders
    GROUP BY user_id
)
SELECT user_id, cnt FROM stats
"""

parsed = Parsed(sql)
# 提取源表和目标表
for index, parsed in enumerate(parsed.parsed_forest):
    print(f"第{index+1}个SQL: {parsed}")
    if parsed.type == "insert" and parsed.query_load:
        query_parsed = parsed.query.parsed
        for source in query_parsed.sources:
            print(f"expr: {source}")
            print(f"源表: {source.table}")

```

#### 2. SQL质量检查
```python
from fastsqlparse import ParsedQuery

sql = "SELECT * FROM users WHERE id = 1"
query = ParsedQuery(sql, "test")

# 检查是否使用SELECT *
if '*' in query.parsed.clause_select:
    print("警告: 使用了SELECT *")

# 检查是否有WHERE条件
has_where = any(c.part == "CLAUSE_WHERE" for c in query.parsed.clauses)
if not has_where:
    print("警告: 缺少WHERE条件")
```

#### 3. SQL格式化服务
```python
from fastsqlparse import Parsed

def format_sql(sql: str, remove_comments: bool = False) -> str:
    """格式化SQL"""
    parsed = Parsed(sql, pure=remove_comments)
    return parsed.format(indent="    ")

# 使用
formatted = format_sql("select * from users where id=1", remove_comments=True)
print(formatted)
```

#### 4. 高性能批量解析
```python
from fastsqlparse import ParsedOne
import time

sqls = [...]  # 大量SQL列表

start = time.time()
for sql in sqls:
    try:
        query = ParsedOne(sql)
        # 处理查询
    except Exception as e:
        print(f"解析失败: {e}")

elapsed = time.time() - start
print(f"解析了{len(sqls)}条SQL，耗时{elapsed:.2f}秒")
print(f"PPS: {len(sqls)/elapsed:.2f}")
```

---

## API参考

### 核心类

#### Parsed - 通用SQL解析器

```python
from fastsqlparse import Parsed

parsed = Parsed(
    sql_statements: str,  # SQL字符串
    file: str = None,     # 可选：SQL文件路径
    name: str = None,     # 可选：名称标识
    pure: bool = False,   # 控制注释处理：True 去除 `--`/`/* ... */` 注释；False 保留注释
    dialect: str = "ansi" # SQL 方言：ansi/mysql/postgresql/sqlite/doris
)
```

**属性**:
- `parsed_forest`: List[Statement] - 解析后的语句列表
- `statements`: List[str] - 原始SQL语句列表
- `name`: str - 名称标识

**方法**:
- `tokens()`: List[Token] - 获取Token列表
- `AST()`: str - 获取JSON格式的AST
- `format(indent: str = "    ")`: str - 格式化SQL
- `content()`: str - 获取原始SQL内容

#### ParsedOne - 单语句SQL解析器

```python
from fastsqlparse import ParsedOne

parsed = ParsedOne(
    sql_statements: str,  # SQL字符串
    dialect: str = "ansi" # SQL 方言：ansi/mysql/postgresql/sqlite/doris
)
```

**属性**:
- `parsed`: AbstractParsed - 解析后的结构对象（可能是ParsedQuery、ParsedInsert等）
- `type`: str - 语句类型（"query", "insert", "update", "delete", "create", "view"等）

**方法**:
- `tokens()`: List[Token] - 获取Token列表
- `AST()`: str - 获取JSON格式的AST
- `format(indent: str = "    ")`: str - 格式化SQL

#### ParsedQuery - SELECT专用解析器

```python
from fastsqlparse import ParsedQuery

query = ParsedQuery(
    statement: str,  # SELECT语句
    name: str = None,
    pure: bool = False,    # 控制注释处理：True 去除 `--`/`/* ... */` 注释；False 保留注释
    dialect: str = "ansi"  # SQL 方言：ansi/mysql/postgresql/sqlite/doris
)
```

**属性**:
- `name`: str - 语句名称标识
- `statement` - 查询语句
- `level` - 嵌套层级
- `super`: str  - 父级名称标识
- `parent`: ParsedAbstract - 父级解析
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
    - `subquery`: Dict[str, ParsedQuery] - 子查询列表
  - UNION 形态：
    - `T`: str - 语句类型，通常为 `UNIONS`
    - `unions`: List[ParsedQuery | str] - UNION查询列表

**静态方法**:
- `tokenize(statement: str, dialect: DialectType = DialectType.ANSI)`: List[Tuple[str, str, int]] - 快速词法分析
- `parse_dependence(statement: str, dialect: str = "ansi")`: List[str] - 提取表血缘/依赖

#### ParsedInsert - INSERT专用解析器

```python
from fastsqlparse import ParsedInsert

insert = ParsedInsert(
    statement: str,  # INSERT语句
    pure: bool = False,    # 控制注释处理：True 去除 `--`/`/* ... */` 注释；False 保留注释
    dialect: str = "ansi"  # SQL 方言：ansi/mysql/postgresql/sqlite/doris
)
```

**属性**:
- `name`: str - 目标表名
- `columns`: List[str] - 插入的列
- `values`: List[str] - 插入的值
- `query`: ParsedQuery - 查询解析对象（INSERT...SELECT时）
- `query_load`: bool - 是否有查询加载
- `main_stmt`: str - 主语句
- `cte`: ParsedWithStmt - CTE解析对象（INSERT语句级别的CTE，定义在INSERT之前的WITH子句）。注意：此对象的属性与ParsedQuery.cte不同，主要通过 `.units` 访问CTE单元列表。
- `cte_stmt`: str - CTE语句
- `query_stmt`: str - 查询语句

**静态方法**:
- `tokenize(statement: str, dialect: DialectType = DialectType.ANSI)`: List[Tuple[str, str, int]]

### 工具函数

#### strip_comments(sql: str) -> str
去除SQL中的注释（strip comments）

```python
from fastsqlparse import strip_comments

clean_sql = strip_comments("SELECT * FROM users -- comment")
# 结果: "SELECT * FROM users"
```

#### tokenize系列函数

```python
from fastsqlparse import (
    tokenize,
    tokenize_query,
    tokenize_cte,
    tokenize_insert,
    tokenize_update,
    tokenize_delete,
    tokenize_view
)

# 通用tokenizer（dialect 为 DialectType，默认 DialectType.ANSI）
tokens = tokenize(sql)

# 专用tokenizer (更快)
tokens = tokenize_query("SELECT * FROM users", dialect=DialectType.MYSQL)
tokens = tokenize_cte("WITH cte AS (...)")
tokens = tokenize_insert("INSERT INTO ...")
```

### 方言（Dialects）

`dialect` 用于指定解析与词法分析的 SQL 方言（默认 `"ansi"`）。所有解析器构造函数接受字符串形式的 `dialect`；`tokenize` 类方法与 `ParsedQuery.parse_dependence` 接受 `DialectType`（默认 `DialectType.ANSI`）。

支持的方言：`ansi`、`mysql`、`postgresql`、`sqlite`、`doris`（见 `fastsqlparse.conf` 中的 `Dialects` 枚举与 `DIALECT_*` 常量）。

```python
from fastsqlparse import Parsed, ParsedQuery, Dialects, DialectType

parsed = Parsed(sql, dialect=Dialects.MYSQL.value)          # "mysql"
query = ParsedQuery(sql, "q", dialect="postgresql")
ParsedQuery.tokenize(sql, dialect=DialectType.MYSQL)        # 类型化 DialectType
ParsedQuery.parse_dependence(sql, dialect="mysql")
```

### Token结构

```python
class Token:
    type: str      # Token类型
    value: str     # Token值
    at: int        # 位置索引
```

**Token类型**:
- `KEYWORD`: SQL关键字 (SELECT, FROM, WHERE等)
- `IDENTIFIER`: 标识符 (表名、列名、别名)
- `NUMBER/STRING`: 字面量 (数字、字符串)
- `WHITESPACE`: 空白字符
- `SUBQUERY`: 子查询
- `OPERATOR`: 运算符
- `COMMENT`: 注释

### AST结构

AST以JSON字符串形式返回，包含：
- 查询子句 (SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT)
- CTE定义
- 列信息
- 数据源信息
- 联合查询信息
- 子查询信息

```python
import json
from fastsqlparse import Parsed

sql = """SELECT * FROM users WHERE id = 1"""
parsed = Parsed(sql)
ast_json = parsed.AST()
ast_obj = json.loads(ast_json)

# 访问AST
print(ast_obj.keys())
```

---

## 安装指南

### 从PyPI安装 (推荐)

```bash
pip install fast-pysqlparse
```

### 从源码安装

```bash
git clone https://github.com/Nohaltsail/fast-pysqlparse.git
cd fast-pysqlparse
pip install build
python -m build
cd dist
pip install fast_pysqlparse-*.whl
```

### 预编译扩展

项目已提供多平台预编译扩展：

**Windows** (.pyd):
- `pysqlparser.cp310-win_amd64.pyd` (Python 3.10)
- `pysqlparser.cp311-win_amd64.pyd` (Python 3.11)
- `pysqlparser.cp312-win_amd64.pyd` (Python 3.12)
- `pysqlparser.cp313-win_amd64.pyd` (Python 3.13)
- `pysqlparser.cp314-win_amd64.pyd` (Python 3.14)

**Linux** (.so):
- `pysqlparser.cpython-310-x86_64-linux-gnu.so`
- `pysqlparser.cpython-311-x86_64-linux-gnu.so`
- `pysqlparser.cpython-312-x86_64-linux-gnu.so`
- `pysqlparser.cpython-313-x86_64-linux-gnu.so`
- `pysqlparser.cpython-314-x86_64-linux-gnu.so`

---


### 类型映射

| Python对象         | 说明        |
|------------------|-----------|
| `DqlSourceExpr`  | 数据源表达式    |
| `DqlColumnExpr`  | 列表达式      |
| `Token`          | 词法单元      |
| `Clause`         | SQL子句     |
| `CommonTableExpr` | 公用表表达式    |
| `QueryStatement`  | 查询语句解析结构体 |

### 错误处理

```python
from fastsqlparse import Parsed

try:
    parsed = Parsed(invalid_sql)
except Exception as e:
    print(f"解析失败: {e}")
```

### 最佳实践

1. **选择合适的解析器**
   - 未知类型或多语句 → `Parsed`
   - 已知SELECT → `ParsedQuery` (层级更少更直观)
   - 已知INSERT → `ParsedInsert`

2. **性能优化**
   - 使用 `pure=True` 在解析前移除 `--` 和 `/* ... */` 注释（通常更快，且输出不含注释）
   - 缓存解析结果避免重复解析
   - 仅需词法信息时使用`tokenize()`静态方法

3. **内存优化**
   - 大SQL分批解析
   - 及时释放不需要的解析结果
   - 使用生成器处理大量SQL

---

## 详细文档

完整的API文档请参考: [API_DOC_CN.md](https://github.com/Nohaltsail/fast-pysqlparse/blob/main/API_DOC_CN.md)

---

## 贡献指南

欢迎贡献！您可以通过以下方式参与：

- 报告Bug
- 提出新功能建议
- 改进文档
- 提交Pull Request

### 开发环境设置

```bash
git clone https://github.com/Nohaltsail/fast-pysqlparse.git
cd fast-pysqlparse
pip install -e .
pytest test/
```

---

## 许可证

本项目采用 **MIT 许可证** - 详情请参见 [LICENSE](LICENSE) 文件。

### 关于动态库的说明

本项目当前分发预编译动态库（`.pyd` 和 `.so`）。
这些动态库对应的 C++ 源代码目前暂未公开，计划在后续版本开放。

完整补充说明请参见 [LICENSE](LICENSE) 文件。

**您也可以直接使用源码中的动态库二次开发您自己的SQL解析库。**
