"""
fast-fastsqlparse
Author:Cynohalt 2972906133@qq.com
This module is used for parsing SQL statements.
You should use UTF8-encoding statements string or sql file.
"""

from fastsqlparse.statement import *
from fastsqlparse.sql import Sql
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
