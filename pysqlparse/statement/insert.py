from typing import List, Any, Tuple

import pysqlparse.pysqlparser as parser
from pysqlparse.conf import DEFAULT_FORMAT_INDENT


class Insert(object):
    """
    A SQL INSERT statement parser and structured representation.

    This class parses SQL INSERT statements and provides programmatic access to:
    - Target table information
    - Column/value mappings
    - Query-based inserts (INSERT...SELECT)
    - Common Table Expressions (CTEs)
    - Original SQL text and syntactic components

    The parser handles both explicit value inserts and query-based inserts:
    - Value inserts: INSERT INTO table (col1, col2) VALUES (val1, val2)
    - Query inserts: INSERT INTO table SELECT * FROM source_table
    - Bulk inserts: INSERT INTO table VALUES (v1,v2), (v3,v4), ...
    """

    __attrs__ = (
        "raw",
        "name",
        "query_load",
        "query",
        "columns",
        "values",
        "main_stmt",
        "cte_stmt",
        "query_stmt"
    )

    __callables__ = (
        "ast",
        "format",
        "tokens"
    )

    def __init__(self, statement: str, pure: bool = False):
        """
        Initialize an Insert instance by parsing an SQL INSERT statement.

        Args:
            statement: Complete SQL INSERT statement to parse
                     Examples:
                       "INSERT INTO t1 VALUES (1, 'a')"
                       "INSERT INTO t1 SELECT * FROM t2"
            pure: If True, strips comments and non-essential elements during parsing.
                  Default False preserves original SQL structure.

        Raises:
            SQLSyntaxError: For malformed INSERT statements
            ParserError: For unsupported INSERT variants
        """
        self.__stmt__ = parser.insert(statement, pure)
        self.name = ""
        for m in Insert.__callables__:
            setattr(self, m, getattr(self.__stmt__, m))
        for name in Insert.__attrs__:
            attr = getattr(self.__stmt__, name)
            setattr(self, name, attr)
        self._stmt = ""
        self._head = ""

    def __repr__(self) -> str:
        """Official string representation showing class and target table."""
        return repr(f"<class {self.__class__.__name__} name='{self.name}'>")

    def format(self, indent: str = DEFAULT_FORMAT_INDENT*' ', init_indent: int = 0) -> str:
        """
        Generate a consistently formatted version of the INSERT statement.

        Args:
            indent: Whitespace string for each indentation level
                   (default: 4 spaces)
            init_indent: Base indentation level (default: 0)

        Returns:
            Professionally formatted SQL string with:
            - Consistent indentation
            - Standardized keyword casing
            - Improved readability
        """
        pass

    def ast(self) -> str:
        """
        Generate an abstract syntax tree (AST) of the INSERT statement.

        Returns:
            JSON string containing structured representation with:
            - Target table metadata
            - Column/value mappings
            - Query components (for INSERT...SELECT)
            - CTE definitions (if present)
            - Statement modifiers (IGNORE, ON DUPLICATE KEY, etc.)
        """
        pass

    def tokens(self) -> List[Any]:
        """
        Retrieve lexical tokens from the parsed statement.

        Returns:
            List of token objects containing:
            - Token type (keyword, identifier, literal, etc.)
            - Text value
            - Position information (line, column)

        Note: Token granularity depends on the underlying SQL dialect parser.
        """
        pass

    @classmethod
    def tokenize(cls, statement: str) -> List[Tuple[str, str, str]]:
        """
        Perform lightweight lexical analysis of an INSERT statement.

        Args:
            statement: SQL INSERT statement to tokenize

        Returns:
            Tuple of tokens

        Useful for quick analysis without full parsing overhead.
        """
        return parser.Insert.tokenize(statement)
