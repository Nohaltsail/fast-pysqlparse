"""
fast-sqlparse
Author: sail2345@qq.com
github: https://github.com/Nohaltsail/fast-pysqlparse
This module is used for parsing SQL statements.
You should use UTF8-encoding statements string or sql file.
"""

from fastsqlparse.statement import *
from fastsqlparse.parser import Parsed, ParsedOne
from fastsqlparse.pysqlparser import AbstractStatement as ParsedAbstract
from fastsqlparse.pysqlparser import (
    format,
    strip_note
)

tokenize: callable = ParsedAbstract.tokenize
tokenize_query: callable = ParsedQuery.tokenize
tokenize_insert: callable = ParsedInsert.tokenize
tokenize_update: callable = ParsedUpdate.tokenize
tokenize_delete: callable = ParsedDelete.tokenize
tokenize_cte: callable = ParsedCTE.tokenize
tokenize_view: callable = ParsedView.tokenize


__all__ = (
    Parsed,
    ParsedOne,
    ParsedAbstract,
    ParsedCTE,
    ParsedInsert,
    ParsedQuery,
    ParsedCreate,
    ParsedView,
    ParsedUpdate,
    ParsedDelete,
    format,
    strip_note,
    tokenize,
    tokenize_query,
    tokenize_insert,
    tokenize_update,
    tokenize_delete,
    tokenize_cte,
    tokenize_view
)