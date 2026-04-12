"""
fast-sqlparse
Author: sail2345@qq.com
github: https://github.com/Nohaltsail/fast-pysqlparse
This module is used for parsing SQL statements.
You should use UTF8-encoding statements string or sql file.
"""

from fastsqlparse.statement import *
from fastsqlparse.parser import ParsedSQL
from fastsqlparse.pysqlparser import AbstractStatement
from fastsqlparse.pysqlparser import (
    view,
    delete,
    query,
    cte,
    insert,
    update,
    create,
    format,
    strip_note
)
