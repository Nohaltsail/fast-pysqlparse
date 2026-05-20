from typing import List, Any, Tuple
from fastsqlparse import pysqlparser as parser


class ParsedQuery(object):
    """
    Query class is used to parse and process SQL queries.

    This class initializes its attributes by parsing SQL content and provides some methods
    to handle and format SQL queries. It uses the pysqlparser library to parse SQL statements
    and initializes the class attributes based on the parsed results.
    """
    name: str
    raw: str
    super: str
    parent: Any
    level: int
    parsed: Any
    cte: Any
    statement: str

    __attrs__ = (
        "name",
        "raw",
        "super",
        "parent",
        "level",
        "parsed",
        "cte",
        "statement",
    )

    __callables__ = (
        "ast",
        "format",
        "tokens",
        "available_cte"
    )

    def __init__(self, statement: str, name: str, pure: bool = False):
        """
        Initialize the Query object.

        Args:
            statement (str): The SQL content to be parsed.
            name (str): The name associated with the SQL query.
            pure (bool): Parse SQL without note
        """
        self.__stmt__ = parser.query(statement, name, pure)
        self._columns = None
        self.__init_items(self.__stmt__)

    def __init_items(self, stmt):
        """
        Initialize the attributes and methods of the Query object based on the parsed statement.

        Args:
            stmt (object): The parsed SQL statement object.
        """
        for m in ParsedQuery.__callables__:
            setattr(self, m, getattr(stmt, m))
        for name in ParsedQuery.__attrs__:
            attr = getattr(stmt, name)
            setattr(self, name, attr)

    @property
    def columns(self):
        """
        Get the columns of the SQL query.

        Returns:
            list: The list of columns in the SQL query.
        """
        return self._columns

    @staticmethod
    def parse_dependence(statement: str) -> List[str]:
        """
        Parse the dependencies of the SQL statement.

        Args:
            statement (str): The SQL statement to parse.

        Returns:
            list: A list of dependencies.
        """
        return parser.parse_dependence(statement)

    def format(self, indent: str = "    ", init_indent: int = 0) -> str:
        """
        Format the SQL query with indentation.

        Args:
            indent (str): The string used for indentation.
            init_indent (int): The initial level of indentation.

        Returns:
            str: The formatted SQL query.
        """
        pass

    def ast(self) -> str:
        """
        Generate a JSON AST representation of the SQL query.

        Returns:
            str: The JSON AST representation of the SQL query.
        """
        pass

    def tokens(self) -> List[Any]:
        """
        Get the tokens.

        Returns:
            list: List of tokens.
        """
        pass

    def available_cte(self):
        """
        Get all CTEs (Common Table Expressions) available in the current query scope.

        This method retrieves all CTEs that can be referenced within the current query context.
        These CTEs typically come from ancestor ParsedQuery or ParsedInsert objects in the
        query hierarchy, including those defined in WITH clauses at various levels.

        Returns:
            dict: Dictionary containing all accessible CTEs in the current scope.
        """
        pass

    @classmethod
    def tokenize(cls, statement: str) -> List[Tuple[str, str, int]]:
        """
        Perform lexical analysis of a QUERY clause statement.

        Args:
            statement: SQL QUERY statement to tokenize

        Returns:
            Tuple of tokens

        Note: This provides faster analysis than full parsing when only
              lexical information is required.
                """
        return parser.Dql.tokenize(statement)

