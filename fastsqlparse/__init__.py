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

_pysqlparser: Any = import_module("fastsqlparse.pysqlparser")
ParsedAbstract = _pysqlparser.AbstractStatement
format = _pysqlparser.format
strip_note = _pysqlparser.strip_note

tokenize: callable = ParsedAbstract.tokenize
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
    "ParsedSQL",
    "format",
    "strip_note",
    "tokenize",
    "tokenize_query",
    "tokenize_insert",
    "tokenize_update",
    "tokenize_delete",
    "tokenize_cte",
    "tokenize_view"
)