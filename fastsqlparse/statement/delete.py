from typing import Tuple, List, Any

import fastsqlparse.pysqlparser as parser
from fastsqlparse.conf import (
    DialectType,
    DIALECT_ANSI,
    Dialects
)


class ParsedDelete(object):
    """
    A SQL DELETE statement parser and analyzer.

    This class parses SQL DELETE statements and provides structured access to:
    - Target table identification
    - Deletion conditions (WHERE clause)
    - Original SQL text
    - Lexical token analysis
    """

    __attrs__ = (
        "name",
        "raw",
        "condition"
    )

    __callables__ = (
        "tokens",
    )

    def __init__(
            self,
            statement: str,
            pure: bool = False,
            dialect: str = Dialects.ANSI.value
    ):
        """
        Initialize a Delete instance by parsing an SQL DELETE statement.

        Args:
            statement: Complete SQL DELETE statement to parse
                     Example: "DELETE FROM employees WHERE status = 'inactive'"
            pure: Controls SQL comment handling. True strips `--` and
                `/* ... */` comments before parsing, so formatted output and
                token results exclude comments and parsing may be faster.
                False preserves comments.
            dialect: default: ansi. support: mysql/postgresql/sqlite/doris
        """
        self.dialect = dialect
        self.__stmt__ = parser.delete(statement, pure, dialect)
        for m in ParsedDelete.__callables__:
            setattr(self, m, getattr(self.__stmt__, m))
        for n in ParsedDelete.__attrs__:
            setattr(self, n, getattr(self.__stmt__, n))

    def __repr__(self) -> str:
        """Official string representation of the Delete instance."""
        return repr(f"<class {self.__class__.__name__} name='{self.dialect}_DELETE'>")

    def tokens(self) -> List[Any]:
        """
        Retrieve lexical tokens from the parsed DELETE statement.

        Returns:
            List of token dictionaries containing:
            - 'type': Token category (keyword, identifier, operator, etc.)
            - 'value': The actual text value
            - 'position': Tuple of (line_number, column_position)
        """
        pass

    @classmethod
    def tokenize(cls, statement: str, dialect: DialectType = DIALECT_ANSI) -> List[Tuple[str, str, int]]:
        """
        Perform lightweight lexical analysis of a DELETE statement.

        Args:
            statement: SQL DELETE statement to tokenize
            dialect: DialectType, default: DialectType.ANSI
        Returns:
            return tokens of Statements

        Useful for quick analysis without full parsing overhead.
        """
        return parser.Delete.tokenize(statement, dialect)
