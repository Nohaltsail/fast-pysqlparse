from typing import List, Any, Tuple
from pysqlparse import pysqlparser as parser


class Query(object):
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
        "level",
        "union_keys",
        "union_stmt",
        "cte_names",
        "cte_map",
        "statement",
        "subquery",
        "clause_select",
        "clause_source",
        "sources",
        "clause_from",
        "clause_condition",
        "clause_aggregation",
        "clause_sorting",
        "clause_limit",
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
        self.unions = []
        self._columns = None
        self.cte = None
        self.__init_items(self.__stmt__)

    def __init_items(self, stmt):
        """
        Initialize the attributes and methods of the Query object based on the parsed statement.

        Args:
            stmt (object): The parsed SQL statement object.
        """
        for m in Query.__callables__:
            setattr(self, m, getattr(stmt, m))
        for name in Query.__attrs__:
            attr = getattr(stmt, name)
            if name == "cte_names":
                if not attr:
                    continue
                self.cte = dict()
                for n in attr:
                    self.cte[n] = getattr(stmt, "cte_map")[n]
                continue
            if name == "union_keys":
                if not attr:
                    continue
                for i, it in enumerate(attr):
                    self.unions.append(getattr(stmt, "union_stmt")[i])
                    self.unions.append(it)
                self.unions.append(getattr(stmt, "union_stmt")[-1])
                break
            if name == "union_stmt" or name == "cte_map":
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
    def tokenize(cls, statement: str) -> List[Tuple[str, str, str]]:
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

