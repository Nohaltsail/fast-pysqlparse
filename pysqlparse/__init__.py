"""
fast-pysqlparse
Author:Cynohalt 2972906133@qq.com
This module is used for parsing SQL statements.
You should use UTF8-encoding statements string or sql file.
"""

from pysqlparse.statement import *
from pysqlparse.sql import Sql
from pysqlparse.pysqlparser import AbstractStatement
from pysqlparse.pysqlparser import (
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
