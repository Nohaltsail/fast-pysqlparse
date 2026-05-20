"""Benchmark four Python parser libraries with a ~10M PostgreSQL SQL script.

Compared libraries:
- pglast
- fastsqlparse
- sqlglot (postgres dialect)
- sqlparse

Run:
    python test/python_parsers_10m.py --runs 1 --json-out test/results/python_parsers_10m.json
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from typing import Any, Callable

TARGET_SQL_SIZE = 10_000_000


def build_postgres_base_query() -> str:
    return """
WITH recent_orders AS (
    SELECT
        o.order_id,
        o.user_id,
        o.created_at,
        o.status,
        o.amount,
        date_trunc('month', o.created_at) AS order_month,
        row_number() OVER (PARTITION BY o.user_id ORDER BY o.created_at DESC) AS rn
    FROM orders o
    WHERE o.created_at >= NOW() - interval '365 days'
),
monthly_user_stats AS (
    SELECT
        user_id,
        order_month,
        count(*) AS order_count,
        sum(amount) AS total_amount,
        avg(amount) AS avg_amount,
        sum(amount) FILTER (WHERE status = 'paid') AS paid_amount
    FROM recent_orders
    GROUP BY user_id, order_month
)
SELECT
    u.user_id,
    u.country_code,
    ms.order_month,
    ms.order_count,
    ms.total_amount,
    ms.avg_amount,
    coalesce(ms.paid_amount, 0) AS paid_amount,
    CASE
        WHEN ms.total_amount >= 10000 THEN 'platinum'
        WHEN ms.total_amount >= 5000 THEN 'gold'
        WHEN ms.total_amount >= 1000 THEN 'silver'
        ELSE 'bronze'
    END AS user_segment
FROM users u
JOIN monthly_user_stats ms ON u.user_id = ms.user_id
WHERE EXISTS (
    SELECT 1
    FROM payments p
    WHERE p.order_id IN (
        SELECT ro.order_id
        FROM recent_orders ro
        WHERE ro.user_id = u.user_id
    )
)
ORDER BY ms.order_month DESC, ms.total_amount DESC
LIMIT 200;
""".strip()


def generate_large_postgres_sql(target_size: int = TARGET_SQL_SIZE) -> str:
    base = build_postgres_base_query()
    parts: list[str] = []
    total = 0
    while total < target_size:
        parts.append(base)
        total += len(base) + 1
    return "\n".join(parts)


def run_benchmark(name: str, parser_fn: Callable[[str], Any], sql: str, runs: int) -> dict[str, Any]:
    timings: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        parser_fn(sql)
        timings.append(time.perf_counter() - t0)

    avg_sec = statistics.fmean(timings)
    return {
        "name": name,
        "success": True,
        "runs": runs,
        "time_avg_sec": avg_sec,
        "time_min_sec": min(timings),
        "time_max_sec": max(timings),
        "timings_sec": timings,
        "cps": len(sql) / avg_sec if avg_sec > 0 else 0.0,
        "error": None,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare four Python SQL parsers on ~10M SQL")
    parser.add_argument("--runs", type=int, default=1, help="Repetitions per parser")
    parser.add_argument("--json-out", type=str, default="", help="Optional JSON output path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    runs = max(1, args.runs)

    print("=" * 80)
    print("Python Parsers 10M Benchmark (No C Benchmark)")
    print("=" * 80)

    sql = generate_large_postgres_sql()
    print(f"SQL size: {len(sql):,} chars")

    tasks: list[tuple[str, Callable[[str], Any]]] = []

    try:
        from pglast.parser import parse_sql  # type: ignore

        tasks.append(("pglast", parse_sql))
    except Exception as exc:  # noqa: BLE001
        print(f"[skip] pglast: {exc}")

    try:
        from fastsqlparse import Parsed

        tasks.append(("fastsqlparse", lambda s: Parsed(s)))
    except Exception as exc:  # noqa: BLE001
        print(f"[skip] fastsqlparse: {exc}")

    try:
        import sqlglot

        tasks.append(("sqlglot(postgres)", lambda s: sqlglot.parse(s, read="postgres")))
    except Exception as exc:  # noqa: BLE001
        print(f"[skip] sqlglot: {exc}")

    try:
        import sqlparse

        tasks.append(("sqlparse", sqlparse.parse))
    except Exception as exc:  # noqa: BLE001
        print(f"[skip] sqlparse: {exc}")

    if len(tasks) < 4:
        print("Warning: fewer than four parsers available in this environment.")

    results: list[dict[str, Any]] = []
    for name, fn in tasks:
        print("-" * 80)
        print(f"Running: {name} (runs={runs})")
        try:
            result = run_benchmark(name, fn, sql, runs)
            results.append(result)
            print(
                f"{name}: avg={result['time_avg_sec']:.4f}s, "
                f"CPS={result['cps']:,.2f}"
            )
        except Exception as exc:  # noqa: BLE001
            fail = {
                "name": name,
                "success": False,
                "runs": runs,
                "time_avg_sec": 0.0,
                "time_min_sec": 0.0,
                "time_max_sec": 0.0,
                "timings_sec": [],
                "cps": 0.0,
                "error": str(exc),
            }
            results.append(fail)
            print(f"{name}: FAILED")
            print(f"Error: {exc}")

    payload = {
        "benchmark": "python_parsers_10m",
        "sql_size": len(sql),
        "runs": runs,
        "results": results,
    }

    print("-" * 80)
    print("JSON summary:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.json_out:
        out_path = os.path.abspath(args.json_out)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"Saved JSON summary: {out_path}")


if __name__ == "__main__":
    main()

