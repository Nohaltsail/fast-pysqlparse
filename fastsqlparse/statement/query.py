from typing import List, Any, Tuple
from fastsqlparse import pysqlparser as parser


class ParsedQuery(object):
    """
    Query class is used to parse and process SQL queries.

    This class initializes its attributes by parsing SQL content and provides some methods
    to handle and format SQL queries. It uses the pysqlparser library to parse SQL statements
    and initializes the class attributes based on the parsed results.
    """
    __attrs__ = (
        "name",
        "raw",
        "super",
        "parent",
        "level",
        "union_type",
        "unions",
        "cte_list",
        "with",
        "statement",
        "subquery",
        "clause_select",
        "clause_source",
        "sources",
        "clauses",
        "columns"
    )

    __callables__ = (
        "ast",
        "format",
        "tokens"
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
            if name == "cte_list":
                if not attr:
                    continue
                self.cte = dict()
                for n in attr:
                    self.cte[n] = getattr(stmt, "with")[n]
                continue
            if name == "union_type":
                if not attr:
                    continue
                unions = []
                for i, it in enumerate(attr):
                    unions.append(getattr(stmt, "unions")[i])
                    unions.append(it)
                unions.append(getattr(stmt, "unions")[-1])
                self.unions = unions
                if getattr(stmt, "cte_list"):
                    self.cte = dict()
                    for n in getattr(stmt, "cte_list"):
                        self.cte[n] = getattr(stmt, "with")[n]
                break
            if name == "unions" or name == "with":
                continue
            if name == "columns":
                setattr(self, "_columns", attr)
                continue
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

