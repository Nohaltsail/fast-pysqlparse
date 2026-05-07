import os.path

from fastsqlparse.conf import *
from fastsqlparse import pysqlparser


class ParsedOne(pysqlparser.ParsedOne):
    """
    Parse SQL statements, which can be any single statement of:
    CREATE TABLE, SELECT, INSERT, DELETE, VIEW, UPDATE, etc.
    Extract key elements, format, get abstract syntax tree, tokens, etc.
    (Note: Token extraction is currently not supported due to dialect differences in CREATE TABLE statements)

    Parameters:
        sql_statement: SQL statement string to be parsed

    Note:
        If the input SQL string contains multiple statements, only the first valid statement will be parsed.
    """
    def __init__(self, sql_statement):
        super(ParsedOne, self).__init__(sql_statement)

    def AST(self) -> str:
        """
        Get and return Sql AST with json string
        :return: sql AST json string
        """
        return super(ParsedOne, self).AST()

    def format(self, indent=DEFAULT_FORMAT_INDENT*' ') -> str:
        """
        :param indent: indent
        :return: sql statements after format
        """
        return super(ParsedOne, self).format(indent)

    def tokens(self) -> list[pysqlparser.Token]:
        """
        return tokens of Statements
        """
        return super(ParsedOne, self).tokens()


class Parsed(pysqlparser.Parsed):
    """
    Parse SQL statements, which can be any combination or single statement of:
    CREATE TABLE, SELECT, INSERT, DELETE, VIEW, UPDATE, etc.
    Extract key elements, format, get abstract syntax tree, tokens, etc.
    (Note: Token extraction is currently not supported due to dialect differences in CREATE TABLE statements)

    Parameters:
        sql_statements: SQL statement string to be parsed
        file: SQL file
        name: Name for the parsed content
        pure: Whether to ignore comments

    Note:
        Either sql_statements or file must be provided.
        - If only file is provided, the SQL file will be loaded and parsed.
        - If both are provided, sql_statements will be cached to the file.
        - Any invalid statements will be automatically  filtered out and will not appear in the parsed-result-tree.
    """
    def __init__(
            self,
            sql_statements=None,
            file=None,
            name="",
            pure=False
    ):
        if not sql_statements and not file:
            raise Exception("empty SQL statement or file")
        elif not file:
            super(Parsed, self).__init__(sql_statements, pure, False, "", name)
        elif not sql_statements:
            super(Parsed, self).__init__(file, pure, name)
        else:
            file_path = os.path.abspath(file)
            super(Parsed, self).__init__(sql_statements, pure, True, file_path, name)
        self._items = None
        self._statements = None

    def content(self) -> str:
        """
        Get and return the sql statement raw content.
        :return: Raw content.
        """
        return super(Parsed, self).content()

    @property
    def parsedforest(self) -> list[pysqlparser.AbstractStatement]:
        """
        Get and return the sql parsed items attribute for the current object.
        :return: The initialized value of the _items attribute.
        """
        if self._items is None:
            self._items = self.parsed_forest()
        return self._items

    @property
    def name(self) -> str:
        """
        Get and return the sql statement name.
        :return: Sql statement name.
        """
        return super(Parsed, self).name()

    @property
    def statements(self) -> str:
        """
        Get and return the sql statements for the current object.
        :return: All statements of SQL input.
        """
        if self._statements is None:
            self._statements = self.get_statements()
        return self._statements

    def AST(self) -> str:
        """
        Get and return Sql AST with json string
        :return: sql AST json string
        """
        return super(Parsed, self).AST()

    def format(self, indent=DEFAULT_FORMAT_INDENT*' ') -> str:
        """
        :param indent: indent
        :return: sql statements after format
        """
        return super(Parsed, self).format(indent)

    def tokens(self) -> list[pysqlparser.Token]:
        """
        return tokens of Statements
        """
        return super(Parsed, self).tokens()

