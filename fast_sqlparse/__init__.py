"""
fast-fast_sqlparse
Author:Cynohalt 2972906133@qq.com
This module is used for parsing SQL statements.
You should use UTF8-encoding statements string or sql file.
"""

from fast_sqlparse.statement import *
from fast_sqlparse.sql import Sql
from fast_sqlparse.pysqlparser import AbstractStatement
from fast_sqlparse.pysqlparser import (
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
