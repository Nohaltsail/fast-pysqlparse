from typing import List, Tuple, Any
import fastsqlparse.pysqlparser as parser
from fastsqlparse.conf import (
    DialectType,
    DIALECT_ANSI,
    Dialects
)


class ParsedCreate(object):
    """
    A SQL CREATE TABLE statement parser and structured representation.

    This class parses DDL (Data Definition Language) statements for table creation and provides
    programmatic access to table schema components including columns, constraints, and metadata.

    Features:
    - Full CREATE TABLE statement parsing
    - Column schema extraction
    - Primary key identification
    - Table metadata access (comments, etc.)
    - Abstract syntax tree generation
    """

    __attrs__ = (
        "name",
        "raw",
        "comment",
        "pri_key",
        "columns",
    )

    __callables__ = (
        "ast",
    )

    def __init__(
            self,
            statement: str,
            pure: bool = False,
            dialect: str = Dialects.ANSI.value
    ):
        """
        Initialize a TableDDL instance by parsing a CREATE TABLE statement.

        Args:
            statement: Complete SQL CREATE TABLE statement to parse
                     Example: "CREATE TABLE employees (id INT PRIMARY KEY, name VARCHAR(100))"
            pure: Controls SQL comment handling. True strips `--` and
                `/* ... */` comments before parsing, so formatted output and
                token results exclude comments and parsing may be faster.
                False preserves comments.
            dialect: default: ansi. support: mysql/postgresql/sqlite/doris
        """
        self.dialect = dialect
        self.__stmt__ = parser.create(statement, pure, dialect)
        for m in ParsedCreate.__callables__:
            setattr(self, m, getattr(self.__stmt__, m))
        for n in ParsedCreate.__attrs__:
            setattr(self, n, getattr(self.__stmt__, n))

    def __repr__(self) -> str:
        """Official string representation of the TableDDL instance."""
        return repr(f"<class {self.__class__.__name__} name='{self.dialect}_CREATE'>")

    def ast(self) -> str:
        """
        Generate an abstract syntax tree (AST) representation of the table definition.

        Returns:
            JSON string containing the structured representation of:
            - Table metadata (name, storage engine, comments)
            - Column definitions (name, type, constraints)
            - Table constraints (primary keys, foreign keys, etc.)
            - Partitioning and table options if specified
        """
        pass

    def tokens(self) -> List[Any]:
        """
        Retrieve lexical tokens from the parsed CREATE statement.

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
        Perform lightweight lexical analysis of a CREATE statement.

        Args:
            statement: SQL CREATE statement to tokenize
            dialect: DialectType, default: DialectType.ANSI
        Returns:
            return tokens of Statements

        Useful for quick analysis without full parsing overhead.
        """
        return parser.Delete.tokenize(statement, dialect)
