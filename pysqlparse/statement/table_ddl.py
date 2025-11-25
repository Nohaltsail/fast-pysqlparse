import pysqlparse.pysqlparser as parser


class TableDDL(object):
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

    def __init__(self, statement: str):
        """
        Initialize a TableDDL instance by parsing a CREATE TABLE statement.

        Args:
            statement: Complete SQL CREATE TABLE statement to parse
                     Example: "CREATE TABLE employees (id INT PRIMARY KEY, name VARCHAR(100))"
        """
        self.name = ""
        self.__stmt__ = parser.create(statement)
        for m in TableDDL.__callables__:
            setattr(self, m, getattr(self.__stmt__, m))
        for n in TableDDL.__attrs__:
            setattr(self, n, getattr(self.__stmt__, n))

    def __repr__(self) -> str:
        """Official string representation of the TableDDL instance."""
        return repr(f"<class {self.__class__.__name__} name='{self.name}'>")

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
