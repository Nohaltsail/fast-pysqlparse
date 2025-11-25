from typing import Tuple, List, Any

import pysqlparse.pysqlparser as parser


class Update(object):
    """
    A SQL UPDATE statement parser and analyzer.

    This class parses SQL UPDATE statements and provides structured access to:
    - The target table name
    - SET clause field-value assignments
    - WHERE condition expressions
    - Original SQL text
    - Lexical tokens

    Typical usage:
        >>> update = Update("UPDATE employees SET salary = 5000 WHERE dept = 'IT'")
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

    def __init__(self, statement: str):
        """
        Initialize an Update instance by parsing an SQL UPDATE statement.

        Args:
            statement: Complete SQL UPDATE statement to parse
                     Example: "UPDATE table SET col1=val1 WHERE condition"

        Raises:
            SQLSyntaxError: If the input is not a valid UPDATE statement
        """
        self.name = ""
        self.__stmt__ = parser.update(statement)
        for m in Update.__callables__:
            setattr(self, m, getattr(self.__stmt__, m))
        for n in Update.__attrs__:
            setattr(self, n, getattr(self.__stmt__, n))

    def __repr__(self) -> str:
        """Official string representation of the Update instance."""
        return repr(f"<class {self.__class__.__name__} name='{self.name}'>")

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
    def tokenize(cls, statement: str) -> List[Tuple[str, str, str]]:
        """
        Perform lexical analysis of an UPDATE statement without full parsing.

        Args:
            statement: SQL UPDATE statement to tokenize

        Returns:
            Tuple of tokens

        This provides faster analysis when only token-level information is needed.
        """
        return parser.Update.tokenize(statement)