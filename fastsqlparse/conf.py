import os
import pysqlparser
from enum import Enum

__CURRENT_PATH__ = os.path.dirname(os.path.abspath(__file__))

DEFAULT_FORMAT_INDENT = 4


class Dialects(Enum):
    ANSI = "ansi"
    MYSQL = "mysql"
    DORIS = "doris"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"


DialectType = pysqlparser.DIALECT

DIALECT_ANSI = DialectType.ANSI
DIALECT_MYSQL = DialectType.MYSQL
DIALECT_POSTGRESQL = DialectType.PGSQL
DIALECT_SQLITE = DialectType.SQLITE
DIALECT_DORIS = DialectType.DORIS

