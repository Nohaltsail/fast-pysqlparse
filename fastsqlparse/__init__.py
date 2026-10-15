"""
fast-sqlparse
Author: sail2345@qq.com
github: https://github.com/Nohaltsail/fast-pysqlparse
This module is used for parsing SQL statements.
You should use UTF8-encoding statements string or sql file.
"""

from .statement import *
from .parser import Parsed, ParsedOne
from importlib import import_module
from typing import Any
from .conf import (
    Dialects,
    DialectType,
    SUPPORTED_DIALECTS,
    check_dialect
)

_pysqlparser: Any = import_module("fastsqlparse.pysqlparser")
ParsedAbstract = _pysqlparser.AbstractStatement
format = _pysqlparser.format
_strip_note = _pysqlparser.strip_note
strip_comments = _strip_note


def tokenize(statement: str, dialect: DialectType = DialectType.ANSI):
    """
    Tokenize a single SQL statement, whatever its type.

    Convenience wrapper around ``AbstractStatement.tokenize``. Unlike the raw
    native function (whose pybind signature has no default), the dialect
    argument is optional here and defaults to ``DialectType.ANSI``.

    Args:
        statement: SQL statement to tokenize.
        dialect: ``DialectType`` enum, default ANSI.

    Returns:
        list of (token_value, token_type, position) tuples.
    """
    return ParsedAbstract.tokenize(statement, dialect)


tokenize_query: callable = ParsedQuery.tokenize
tokenize_insert: callable = ParsedInsert.tokenize
tokenize_update: callable = ParsedUpdate.tokenize
tokenize_delete: callable = ParsedDelete.tokenize
tokenize_cte: callable = ParsedCTE.tokenize
tokenize_view: callable = ParsedView.tokenize

# Backward-compatible alias used by older quick-test snippets.
ParsedSQL = Parsed


__all__ = (
    "Parsed",
    "ParsedOne",
    "ParsedAbstract",
    "ParsedCTE",
    "ParsedInsert",
    "ParsedQuery",
    "ParsedCreate",
    "ParsedView",
    "ParsedUpdate",
    "ParsedDelete",
    "format",
    "strip_comments",
    "tokenize",
    "tokenize_query",
    "tokenize_insert",
    "tokenize_update",
    "tokenize_delete",
    "tokenize_cte",
    "tokenize_view",
    "Dialects",
    "DialectType",
    "SUPPORTED_DIALECTS",
    "check_dialect"
)