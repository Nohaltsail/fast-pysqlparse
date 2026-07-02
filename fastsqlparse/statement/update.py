from typing import Tuple, List, Any

import fastsqlparse.pysqlparser as parser
from fastsqlparse.conf import (
    DialectType,
    DIALECT_ANSI,
    Dialects
)


class ParsedUpdate(object):
    """
    A SQL UPDATE statement parser and analyzer.

    This class parses SQL UPDATE statements and provides structured access to:
    - The target table name
    - SET clause field-value assignments
    - WHERE condition expressions
    - Original SQL text
    - Lexical tokens

    Typical usage:
        >>> update = ParsedUpdate("UPDATE employees SET salary = 5000 WHERE dept = 'IT'")
        >>> print(update.fields)  # ['salary']
        >>> print(update.values)   # ['5000']
    """

    __attrs__ = (
        "name",
        "raw",
        "condition",
        "fields",
        "values",
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
        Initialize an Update instance by parsing an SQL UPDATE statement.

        Args:
            statement: Complete SQL UPDATE statement to parse
                     Example: "UPDATE table SET col1=val1 WHERE condition"
            pure: Controls SQL comment handling. True strips `--` and
                `/* ... */` comments before parsing, so formatted output and
                token results exclude comments and parsing may be faster.
                False preserves comments.
            dialect: default: ansi. support: mysql/postgresql/sqlite/doris
        Raises:
            SQLSyntaxError: If the input is not a valid UPDATE statement
        """
        self.dialect = dialect
        self.__stmt__ = parser.update(statement, pure, dialect)
        for m in ParsedUpdate.__callables__:
            setattr(self, m, getattr(self.__stmt__, m))
        for n in ParsedUpdate.__attrs__:
            setattr(self, n, getattr(self.__stmt__, n))

    def __repr__(self) -> str:
        """Official string representation of the Update instance."""
        return repr(f"<class {self.__class__.__name__} name='{self.dialect}_UPDATE'>")

    def tokens(self) -> List[Any]:
        """
        Retrieve the lexical tokens from the parsed UPDATE statement.

        Returns:
            List of token objects containing:
            - Token type (keyword, identifier, operator, etc.)
            - Text value
            - Position information (line, column)

        Note:
            The exact token structure depends on the underlying SQL parser implementation.
        """
        pass

    @classmethod
    def tokenize(cls, statement: str, dialect: DialectType = DIALECT_ANSI) -> List[Tuple[str, str, int]]:
        """
        Perform lexical analysis of an UPDATE statement without full parsing.

        Args:
            statement: SQL UPDATE statement to tokenize
            dialect: DialectType, default: DialectType.ANSI
        Returns:
            Tuple of tokens

        This provides faster analysis when only token-level information is needed.
        """
        return parser.Update.tokenize(statement, dialect)
