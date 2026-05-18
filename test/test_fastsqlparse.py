"""
fast-sqlparse 功能测试和API演示
所有测试都封装在独立的方法中
"""
import fastsqlparse
from fastsqlparse import (
    Parsed,
    ParsedOne,
    ParsedQuery,
    ParsedInsert
)
import json
import time


def test_scenario1_basic_query_with_subquery():
    """场景1：普通查询，包含子查询 - 提取source、columns、各种子句"""
    print("\n【场景1】解析体基本结构：使用普通查询，包含子查询")
    print("-" * 80)

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
    query: ParsedQuery = parsed_multi.parsedforest[0]
    parsed = query.parsed
    print(f"parsed: {parsed}")
    print(f"原始SQL:\n{query.raw}")
    print(f"\n提取的sources: {parsed.sources}")
    print(f"提取的columns: {parsed.columns}")
    print(f"SELECT子句: {parsed.clause_select}")
    print(f"子查询: {parsed.subquery}")
    for i, clause in enumerate(parsed.clauses):
        print(clause)
        if clause.part == "CLAUSE_FROM":
            print(f"FROM子句: {clause.clause}")
        elif clause.part == "CLAUSE_WHERE":
            print(f"WHERE子句: {clause.clause}")
        elif clause.part == "CLAUSE_SORT":
            print(f"ORDER子句: {clause.clause}")
        elif clause.part == "CLAUSE_LIMIT":
            print(f"LIMIT子句: {clause.clause}")

    return query


def test_scenario2_cte_aggregation():
    """场景2：临时结果集（聚合查询）- 获取TOKENS和AST"""
    print("\n【场景2】临时结果集（聚合查询）")
    print("-" * 80)

    sql = """WITH sales_summary AS (
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
        print(f"common tables: {query.cte.common_tables}")
        print(f"expressions: {query.cte.expressions}")

    print(f"原始SQL:\n{sql}")
    print(f"\nTOKENS数量: {len(parsed.tokens())}")
    print(f"前5个TOKENS:")
    for i, token in enumerate(parsed.tokens()[:5]):
        print(token)

    print(f"\nAST (JSON格式):")
    ast_str = parsed.AST()
    ast_obj = json.loads(ast_str)
    print(json.dumps(ast_obj, indent=2, ensure_ascii=False)[:500] + "...")

    return parsed


def test_scenario3_union_tokenizer():
    """场景3：临时结果集 + UNION子查询 - tokenizer测试"""
    print("\n【场景3】临时结果集 + UNION子查询 - tokenizer测试")
    print("-" * 80)

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

    # 使用tokenizer进行词法分析
    tokens = ParsedQuery.tokenize(sql)
    print(f"Tokenizer结果 (前10个token):")
    for i, (token_value, token_type, position) in enumerate(tokens[:10]):
        print(f"  {i}: type={token_type}, value='{token_value}', pos={position}")

    print("++++++++++++++++++++++++++++++")
    # query.parsed 结构分析
    parsed_query = ParsedQuery(sql, "test_table")
    parsed = parsed_query.parsed
    print(f"query.parsed: {parsed}")
    if parsed.T == "UNIONS":
        for e in parsed.unions:
            print(f"{e}")
    return tokens


def test_scenario4_insert_cte_select():
    """场景4：INSERT INTO ... CTE SELECT - 提取字段和query对象"""
    print("\n【场景4】INSERT INTO ... CTE SELECT")
    print("-" * 80)

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
    print(f"原始SQL:\n{sql}")
    print(f"\n目标表名: {insert_parsed.name}")
    print(f"插入的列: {insert_parsed.columns}")
    print(f"是否有查询加载: {insert_parsed.query_load}")
    if insert_parsed.query:
        print(f"查询对象类型: {type(insert_parsed.query)}")
        if hasattr(insert_parsed.query, 'sources'):
            print(f"查询的sources: {insert_parsed.query.sources}")
    print(f"insert_parsed.cte: {insert_parsed.cte}")

    print("++++++++++++++++++++++++++++++")
    parsed_query: ParsedQuery = insert_parsed.query
    print(f"parsed_query: {parsed_query}")
    print(f"parsed_query.parsed: {parsed_query.parsed}")
    print(f"parsed_query.cte: {parsed_query.cte}")
    print(f"parsed_query.cte.common_tables: {parsed_query.cte.common_tables}")
    print(f"parsed_query.cte.expressions: {parsed_query.cte.expressions}")
    print(f"parsed_query.parsed.columns: {parsed_query.parsed.columns}")

    return insert_parsed


def test_scenario5_insert_cte_select():
    """场景4：INSERT INTO ... CTE SELECT - 提取字段和query对象"""
    print("\n【场景4】INSERT INTO ... CTE SELECT")
    print("-" * 80)

    sql = """
WITH product_stats AS (
    SELECT 
        product_id,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount
    FROM orders
    GROUP BY product_id
)
INSERT INTO summary_table (product_id, total_amount, avg_amount)
SELECT product_id, total_amount, avg_amount
FROM product_stats
"""

    insert_parsed = ParsedInsert(sql)
    print(f"insert_parsed.cte: {insert_parsed.cte}")
    for cte in insert_parsed.cte.units:
        print(f"cte: {cte}")

    print("++++++++++++++++++++++++++++++")
    parsed_query: ParsedQuery = insert_parsed.query
    print(f"parsed_query: {parsed_query}")
    print(f"parsed_query.parsed: {parsed_query.parsed}")
    print(f"parsed_query.cte: {parsed_query.cte}")
    print(f"parsed_query.available_cte: {parsed_query.available_cte()}")

    return insert_parsed


def test_scenario6_comments_and_formatting():
    """场景5：有注释的查询语句 - 去掉注释，格式化"""
    print("\n【场景5】有注释的查询语句 - 去掉注释，格式化")
    print("-" * 80)

    sql = """
-- 这是用户查询的主注释
SELECT 
    u.user_id,  -- 用户ID
    u.username  -- 用户名
FROM users u  /* 用户表 */
WHERE u.status = 'active'  -- 只查活跃用户
"""

    # 不去掉注释
    parsed_with_comments = Parsed(sql, pure=False)
    print(f"保留注释的格式化结果:\n{parsed_with_comments.format()}")

    # 去掉注释
    parsed_pure = Parsed(sql, pure=True)
    print(f"\n去掉注释的格式化结果:\n{parsed_pure.format()}")

    # 使用strip_note函数
    stripped = fastsqlparse.strip_note(sql)
    print(f"\n仅去除注释:\n{stripped}")

    return {
        'with_comments': parsed_with_comments,
        'pure': parsed_pure,
        'stripped': stripped
    }


def test_performance_comparison():
    """性能测试1：与sqlparse/sqlglot对比"""
    print("\n【性能测试1】解析速度对比 (1359字符SQL)")
    print("-" * 80)

    test_sql = """
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
LIMIT 50, 100
"""

    print(f"测试SQL长度: {len(test_sql)} 字符")

    # 测试fast-sqlparse
    start_time = time.time()
    for _ in range(100):
        parsed = ParsedQuery(test_sql, "test")
    fast_time = time.time() - start_time
    print(f"fast-sqlparse (100次): {fast_time:.4f}秒, 平均: {fast_time/100*1000:.2f}ms/次")

    results = {'fast_sqlparse': fast_time}

    # 测试sqlparse
    try:
        import sqlparse
        start_time = time.time()
        for _ in range(100):
            parsed = sqlparse.parse(test_sql)
        sqlparse_time = time.time() - start_time
        print(f"sqlparse (100次): {sqlparse_time:.4f}秒, 平均: {sqlparse_time/100*1000:.2f}ms/次")
        print(f"加速比: {sqlparse_time/fast_time:.2f}x")
        results['sqlparse'] = sqlparse_time
        results['speedup_vs_sqlparse'] = sqlparse_time/fast_time
    except ImportError:
        print("sqlparse未安装，跳过对比")

    # 测试sqlglot
    try:
        import sqlglot
        start_time = time.time()
        for _ in range(100):
            parsed = sqlglot.parse(test_sql)
        sqlglot_time = time.time() - start_time
        print(f"sqlglot (100次): {sqlglot_time:.4f}秒, 平均: {sqlglot_time/100*1000:.2f}ms/次")
        print(f"加速比: {sqlglot_time/fast_time:.2f}x")
        results['sqlglot'] = sqlglot_time
        results['speedup_vs_sqlglot'] = sqlglot_time/fast_time
    except ImportError:
        print("sqlglot未安装，跳过对比")

    return results


def test_performance_5000_iterations():
    """性能测试2：5000次解析"""
    print("\n【性能测试2】5000次解析SQL")
    print("-" * 80)

    test_sql = """
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
"""

    print(f"SQL长度: {len(test_sql)} 字符")
    iterations = 5000

    start_time = time.time()
    for _ in range(iterations):
        parsed = Parsed(test_sql)
    total_time = time.time() - start_time
    pps = iterations / total_time

    print(f"总耗时: {total_time:.4f}秒")
    print(f"解析次数: {iterations}")
    print(f"PPS (Parse Per Second): {pps:.2f}")
    print(f"平均每次: {total_time/iterations*1000:.4f}ms")

    return {
        'iterations': iterations,
        'sql_length': len(test_sql),
        'total_time': total_time,
        'pps': pps,
        'avg_ms': total_time/iterations*1000
    }


def test_performance_large_sql():
    """性能测试3：1000万字符SQL（10M）解析"""
    print("\n【性能测试3】1000万字符SQL解析")
    print("-" * 80)

    # 生成大SQL
    base_query = """
WITH 
-- CTE 1: 用户基础信息及订单汇总
user_order_summary AS (
    SELECT 
        u.user_id,
        u.username,
        u.email,
        u.registration_date,
        u.user_tier,
        u.country_code,
        COALESCE(SUM(o.total_amount), 0) AS lifetime_value,
        COUNT(DISTINCT o.order_id) AS total_orders,
        MAX(o.order_date) AS last_order_date,
        MIN(o.order_date) AS first_order_date,
        DATEDIFF(MAX(o.order_date), MIN(o.order_date)) AS customer_lifespan_days
    FROM users u
    LEFT JOIN orders o ON u.user_id = o.user_id
    WHERE u.registration_date >= '2020-01-01'
    GROUP BY u.user_id, u.username, u.email, u.registration_date, u.user_tier, u.country_code
),

-- CTE 2: 订单明细及产品分类
order_product_detail AS (
    SELECT 
        o.order_id,
        o.user_id,
        o.order_date,
        o.total_amount AS order_amount,
        p.product_id,
        p.product_name,
        p.category_id,
        pc.category_name,
        pc.parent_category_id,
        oi.quantity,
        oi.unit_price,
        (oi.quantity * oi.unit_price) AS line_total,
        ROW_NUMBER() OVER (PARTITION BY o.user_id ORDER BY o.order_date DESC) AS order_rank_for_user
    FROM orders o
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    INNER JOIN product_categories pc ON p.category_id = pc.category_id
    WHERE o.order_status IN ('COMPLETED', 'SHIPPED', 'DELIVERED')
),

-- CTE 3: 用户品类偏好分析（含窗口函数）
user_category_preference AS (
    SELECT 
        user_id,
        category_id,
        category_name,
        SUM(line_total) AS category_spend,
        COUNT(DISTINCT order_id) AS category_orders,
        RANK() OVER (PARTITION BY user_id ORDER BY SUM(line_total) DESC) AS category_rank,
        PERCENT_RANK() OVER (PARTITION BY user_id ORDER BY SUM(line_total) DESC) AS category_percent_rank,
        SUM(SUM(line_total)) OVER (PARTITION BY user_id) AS user_total_spend,
        ROUND(100.0 * SUM(line_total) / SUM(SUM(line_total)) OVER (PARTITION BY user_id), 2) AS category_share_percent
    FROM order_product_detail
    GROUP BY user_id, category_id, category_name
),

-- CTE 4: 高价值用户标识（递归CTE演示层级结构）
user_hierarchy AS (
    SELECT 
        user_id,
        username,
        user_tier,
        0 AS referral_level,
        CAST(username AS CHAR(500)) AS referral_path
    FROM users
    WHERE referred_by_user_id IS NULL
    
    UNION ALL
    
    SELECT 
        u.user_id,
        u.username,
        u.user_tier,
        uh.referral_level + 1,
        CONCAT(uh.referral_path, ' -> ', u.username)
    FROM users u
    INNER JOIN user_hierarchy uh ON u.referred_by_user_id = uh.user_id
    WHERE uh.referral_level < 5
),

-- CTE 5: 复杂聚合计算（月度趋势）
monthly_trend_analysis AS (
    SELECT 
        DATE_FORMAT(order_date, '%Y-%m') AS order_month,
        user_tier,
        country_code,
        COUNT(DISTINCT opd.user_id) AS active_customers,
        COUNT(DISTINCT opd.order_id) AS total_orders,
        SUM(opd.order_amount) AS total_revenue,
        AVG(opd.order_amount) AS avg_order_value,
        SUM(opd.quantity) AS total_units_sold,
        SUM(CASE WHEN opd.category_id IN (1, 2, 3) THEN opd.line_total ELSE 0 END) AS electronics_revenue,
        SUM(CASE WHEN opd.category_id IN (4, 5, 6) THEN opd.line_total ELSE 0 END) AS clothing_revenue,
        SUM(CASE WHEN opd.category_id IN (7, 8, 9, 10) THEN opd.line_total ELSE 0 END) AS home_goods_revenue,
        LAG(SUM(opd.order_amount), 1) OVER (PARTITION BY user_tier, country_code ORDER BY DATE_FORMAT(order_date, '%Y-%m')) AS prev_month_revenue,
        LEAD(SUM(opd.order_amount), 1) OVER (PARTITION BY user_tier, country_code ORDER BY DATE_FORMAT(order_date, '%Y-%m')) AS next_month_revenue
    FROM order_product_detail opd
    INNER JOIN user_order_summary uos ON opd.user_id = uos.user_id
    GROUP BY DATE_FORMAT(order_date, '%Y-%m'), user_tier, country_code
)

-- ========== 主查询：多层嵌套 + UNION ALL ==========

-- 第一部分：高价值用户分析报表
SELECT 
    'HIGH_VALUE_USER_REPORT' AS report_type,
    uos.user_id,
    uos.username,
    uos.user_tier,
    uos.country_code,
    uos.lifetime_value,
    uos.total_orders,
    uos.customer_lifespan_days,
    uh.referral_level,
    uh.referral_path,
    ucp.category_name AS top_category,
    ucp.category_spend AS top_category_spend,
    ucp.category_share_percent AS top_category_share,
    CASE 
        WHEN uos.lifetime_value > 10000 AND uos.total_orders > 50 THEN 'PLATINUM'
        WHEN uos.lifetime_value > 5000 AND uos.total_orders > 20 THEN 'GOLD'
        WHEN uos.lifetime_value > 1000 AND uos.total_orders > 5 THEN 'SILVER'
        ELSE 'BRONZE'
    END AS customer_segment,
    (SELECT COUNT(*) FROM order_product_detail opd2 
     WHERE opd2.user_id = uos.user_id AND opd2.order_rank_for_user <= 3) AS recent_orders_count,
    (SELECT AVG(line_total) FROM order_product_detail opd3 
     WHERE opd3.user_id = uos.user_id) AS avg_line_item_value
FROM user_order_summary uos
LEFT JOIN user_hierarchy uh ON uos.user_id = uh.user_id
LEFT JOIN user_category_preference ucp ON uos.user_id = ucp.user_id AND ucp.category_rank = 1
WHERE uos.lifetime_value > 500
  AND uos.user_id IN (
      SELECT DISTINCT user_id 
      FROM order_product_detail 
      WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
  )
  AND EXISTS (
      SELECT 1 FROM order_product_detail opd4 
      WHERE opd4.user_id = uos.user_id 
      AND opd4.category_id IN (1, 2, 3)
      HAVING COUNT(*) >= 2
  )

UNION ALL

-- 第二部分：月度趋势报表（带环比计算）
SELECT 
    'MONTHLY_TREND_REPORT' AS report_type,
    NULL AS user_id,
    CONCAT(order_month, ' - ', user_tier, ' - ', country_code) AS username,
    user_tier,
    country_code,
    total_revenue AS lifetime_value,
    total_orders,
    NULL AS customer_lifespan_days,
    NULL AS referral_level,
    NULL AS referral_path,
    NULL AS top_category,
    NULL AS top_category_spend,
    NULL AS top_category_share,
    NULL AS customer_segment,
    NULL AS recent_orders_count,
    ROUND((total_revenue - prev_month_revenue) / NULLIF(prev_month_revenue, 0) * 100, 2) AS mom_growth_percent
FROM monthly_trend_analysis
WHERE order_month >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 12 MONTH), '%Y-%m')
  AND active_customers >= 10

UNION ALL

-- 第三部分：品类交叉分析（复杂子查询嵌套）
SELECT 
    'CATEGORY_CROSS_ANALYSIS' AS report_type,
    NULL AS user_id,
    CONCAT(pc1.category_name, ' + ', pc2.category_name) AS username,
    NULL AS user_tier,
    NULL AS country_code,
    NULL AS lifetime_value,
    COUNT(DISTINCT opd1.user_id) AS total_orders,
    NULL AS customer_lifespan_days,
    NULL AS referral_level,
    NULL AS referral_path,
    CONCAT(pc1.category_name, ' & ', pc2.category_name) AS top_category,
    SUM(opd1.line_total + opd2.line_total) AS top_category_spend,
    NULL AS top_category_share,
    'CROSS_SELL_OPPORTUNITY' AS customer_segment,
    NULL AS recent_orders_count,
    NULL AS mom_growth_percent
FROM (
    SELECT user_id, category_id, order_id, line_total
    FROM order_product_detail
    WHERE category_id IN (SELECT category_id FROM product_categories WHERE parent_category_id IS NOT NULL)
) opd1
INNER JOIN (
    SELECT user_id, category_id, order_id, line_total
    FROM order_product_detail
    WHERE category_id IN (SELECT category_id FROM product_categories WHERE parent_category_id IS NOT NULL)
) opd2 ON opd1.user_id = opd2.user_id 
       AND opd1.order_id = opd2.order_id 
       AND opd1.category_id < opd2.category_id
INNER JOIN product_categories pc1 ON opd1.category_id = pc1.category_id
INNER JOIN product_categories pc2 ON opd2.category_id = pc2.category_id
GROUP BY pc1.category_name, pc2.category_name
HAVING COUNT(DISTINCT opd1.user_id) >= 5

UNION ALL

-- 第四部分：用户生命周期价值分段统计（多层聚合）
SELECT 
    'LTV_SEGMENT_REPORT' AS report_type,
    NULL AS user_id,
    ltv_segment AS username,
    NULL AS user_tier,
    NULL AS country_code,
    NULL AS lifetime_value,
    NULL AS total_orders,
    NULL AS customer_lifespan_days,
    NULL AS referral_level,
    NULL AS referral_path,
    NULL AS top_category,
    NULL AS top_category_spend,
    NULL AS top_category_share,
    NULL AS customer_segment,
    NULL AS recent_orders_count,
    NULL AS mom_growth_percent
FROM (
    SELECT 
        CASE 
            WHEN lifetime_value >= 10000 THEN '10000+'
            WHEN lifetime_value >= 5000 THEN '5000-9999'
            WHEN lifetime_value >= 1000 THEN '1000-4999'
            WHEN lifetime_value >= 100 THEN '100-999'
            ELSE '0-99'
        END AS ltv_segment,
        COUNT(*) AS user_count,
        AVG(lifetime_value) AS avg_ltv_in_segment,
        SUM(lifetime_value) AS total_ltv_in_segment,
        AVG(total_orders) AS avg_orders_in_segment,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY lifetime_value) OVER () AS median_ltv_overall
    FROM user_order_summary
    WHERE total_orders > 0
    GROUP BY ltv_segment
) ltv_stats
CROSS JOIN (
    SELECT AVG(lifetime_value) AS overall_avg_ltv FROM user_order_summary WHERE total_orders > 0
) overall_stats

UNION ALL

-- 第五部分：用户留存率分析（多层嵌套子查询 + 自连接）
SELECT 
    'RETENTION_COHORT_REPORT' AS report_type,
    NULL AS user_id,
    CONCAT(cohort.cohort_month, ' - Month ', cohort.months_since) AS username,
    NULL AS user_tier,
    NULL AS country_code,
    NULL AS lifetime_value,
    cohort.total_users_in_cohort AS total_orders,
    NULL AS customer_lifespan_days,
    NULL AS referral_level,
    NULL AS referral_path,
    NULL AS top_category,
    NULL AS top_category_spend,
    ROUND(100.0 * COUNT(DISTINCT active.user_id) / cohort.total_users_in_cohort, 2) AS top_category_share,
    NULL AS customer_segment,
    NULL AS recent_orders_count,
    NULL AS mom_growth_percent
FROM (
    SELECT 
        DATE_FORMAT(first_order_date, '%Y-%m') AS cohort_month,
        user_id,
        TIMESTAMPDIFF(MONTH, first_order_date, order_date) AS months_since
    FROM user_order_summary
    CROSS JOIN orders ON user_order_summary.user_id = orders.user_id
    WHERE first_order_date IS NOT NULL
) active
RIGHT JOIN (
    SELECT 
        DATE_FORMAT(first_order_date, '%Y-%m') AS cohort_month,
        COUNT(DISTINCT user_id) AS total_users_in_cohort
    FROM user_order_summary
    WHERE first_order_date IS NOT NULL
    GROUP BY DATE_FORMAT(first_order_date, '%Y-%m')
) cohort ON active.cohort_month = cohort.cohort_month
WHERE active.months_since BETWEEN 0 AND 12
GROUP BY cohort.cohort_month, active.months_since, cohort.total_users_in_cohort

ORDER BY report_type, username
LIMIT 1000;
"""

    large_sql_parts = []
    for i in range(1000):
        large_sql_parts.append(base_query)

    large_sql = ";\n".join(large_sql_parts)
    print(f"大SQL长度: {len(large_sql):,} 字符")

    # 测试fast-sqlparse
    start_time = time.time()
    try:
        parsed_large = Parsed(large_sql)
        fast_time = time.time() - start_time
        fast_cps = len(large_sql) / fast_time if fast_time > 0 else 0

        print(f"fast-sqlparse 总耗时: {fast_time:.4f}秒")
        print(f"fast-sqlparse CPS (Characters Per Second): {fast_cps:,.2f}")
        print(f"fast-sqlparse 解析成功！")

        results = {
            'sql_length': len(large_sql),
            'fast_sqlparse_time': fast_time,
            'fast_sqlparse_cps': fast_cps,
            'success': True
        }
    except Exception as e:
        fast_time = time.time() - start_time
        print(f"fast-sqlparse 解析失败: {str(e)}")
        print(f"fast-sqlparse 耗时: {fast_time:.4f}秒")

        results = {
            'sql_length': len(large_sql),
            'fast_sqlparse_time': fast_time,
            'success': False,
            'error': str(e)
        }

    # 测试sqlparse
    try:
        import sqlparse
        start_time = time.time()
        parsed_sqlparse = sqlparse.parse(large_sql)
        sqlparse_time = time.time() - start_time
        sqlparse_cps = len(large_sql) / sqlparse_time if sqlparse_time > 0 else 0

        print(f"\nsqlparse 总耗时: {sqlparse_time:.4f}秒")
        print(f"sqlparse CPS (Characters Per Second): {sqlparse_cps:,.2f}")
        print(f"sqlparse 解析成功！")
        print(f"相比fast-sqlparse加速比: {sqlparse_time/fast_time:.2f}x")

        results['sqlparse_time'] = sqlparse_time
        results['sqlparse_cps'] = sqlparse_cps
        results['speedup_vs_sqlparse'] = sqlparse_time/fast_time
    except ImportError:
        print("\nsqlparse未安装，跳过对比")
    except Exception as e:
        sqlparse_time = time.time() - start_time
        print(f"\nsqlparse 解析失败: {str(e)}")
        print(f"sqlparse 耗时: {sqlparse_time:.4f}秒")
        results['sqlparse_time'] = sqlparse_time
        results['sqlparse_error'] = str(e)

    # 测试sqlglot
    try:
        import sqlglot
        start_time = time.time()
        # 注意：对于超大SQL，可能需要分割处理或调整配置
        parsed_sqlglot = sqlglot.parse(large_sql)
        sqlglot_time = time.time() - start_time
        sqlglot_cps = len(large_sql) / sqlglot_time if sqlglot_time > 0 else 0

        print(f"\nsqlglot 总耗时: {sqlglot_time:.4f}秒")
        print(f"sqlglot CPS (Characters Per Second): {sqlglot_cps:,.2f}")
        print(f"sqlglot 解析成功！")
        print(f"相比fast-sqlparse加速比: {sqlglot_time/fast_time:.2f}x")

        results['sqlglot_time'] = sqlglot_time
        results['sqlglot_cps'] = sqlglot_cps
        results['speedup_vs_sqlglot'] = sqlglot_time/fast_time
    except ImportError:
        print("\nsqlglot未安装，跳过对比")
    except Exception as e:
        sqlglot_time = time.time() - start_time
        print(f"\nsqlglot 解析失败: {str(e)}")
        print(f"sqlglot 耗时: {sqlglot_time:.4f}秒")
        results['sqlglot_time'] = sqlglot_time
        results['sqlglot_error'] = str(e)

    return results


def run_all_tests():
    """运行所有测试"""
    print("=" * 80)
    print("一、功能展示")
    print("=" * 80)

    # 功能测试
    test_scenario1_basic_query_with_subquery()
    test_scenario2_cte_aggregation()
    test_scenario3_union_tokenizer()
    test_scenario4_insert_cte_select()
    test_scenario5_insert_cte_select()
    test_scenario6_comments_and_formatting()

    print("\n\n" + "=" * 80)
    print("二、性能验证")
    print("=" * 80)
    # 性能测试
    perf_results = dict()
    perf_results['comparison'] = test_performance_comparison()
    perf_results['5000_iterations'] = test_performance_5000_iterations()
    perf_results['large_sql'] = test_performance_large_sql()

    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    
    return perf_results


if __name__ == "__main__":
    results = run_all_tests()
