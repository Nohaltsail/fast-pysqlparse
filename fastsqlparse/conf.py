import os
import warnings
from enum import Enum

from fastsqlparse import pysqlparser

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


#: Dialect names accepted by every ``dialect`` parameter (case-sensitive).
SUPPORTED_DIALECTS = frozenset(d.value for d in Dialects)


def check_dialect(dialect: str) -> str:
    """
    Check a dialect name before handing it to the native layer, and return it
    unchanged.

    Dialect handling is lenient by design: an unknown or empty dialect string
    falls back to ``ansi`` in the native parser. This check keeps that behavior
    but emits a ``UserWarning`` for unrecognized names — usually a typo such as
    ``"postgre"`` or ``"MySQL"`` — so the silent fallback is at least visible.
    The warning is deduplicated per call site by the ``warnings`` machinery, so
    batch parsing stays quiet after the first occurrence.

    Args:
        dialect: dialect name, e.g. ``"ansi"``, ``"mysql"``.

    Returns:
        The dialect string, unchanged (the native layer performs the fallback).

    Raises:
        TypeError: if ``dialect`` is not a str.
    """
    if not isinstance(dialect, str):
        raise TypeError(
            f"dialect must be a str, got {type(dialect).__name__}"
        )
    if dialect not in SUPPORTED_DIALECTS:
        warnings.warn(
            f"Unknown SQL dialect: {dialect!r}; falling back to 'ansi'. "
            f"Supported dialects: {', '.join(sorted(SUPPORTED_DIALECTS))}.",
            stacklevel=3,
        )
    return dialect

