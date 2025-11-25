import os.path

from pysqlparse.conf import *
from pysqlparse import pysqlparser


class Sql(pysqlparser.Sql):
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

    Note: Either sql_statements or file must be provided.
    - If only file is provided, the SQL file will be loaded and parsed.
    - If both are provided, sql_statements will be cached to the file.
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
            super(Sql, self).__init__(sql_statements, False, pure, name)
        elif not sql_statements:
            super(Sql, self).__init__(file, pure, name)
        else:
            file_path = os.path.abspath(file)
            super(Sql, self).__init__(sql_statements, True, file_path, name)
        self._items = None
        self._statements = None

    @property
    def items(self):
        """
        Get and return the sql items attribute for the current object.
        :return: The initialized value of the _items attribute.
        """
        if self._items is None:
            self._items = self.get_items()
        return self._items

    @property
    def statements(self):
        """
        Get and return the sql statements for the current object.
        :return: All statements of SQL input.
        """
        if self._statements is None:
            self._statements = self.get_statements()
        return self._statements

    def AST(self):
        """
        Get and return Sql AST with json string
        :return: sql AST json string
        """
        return super(Sql, self).AST()

    def format(self, indent=DEFAULT_FORMAT_INDENT*' '):
        """
        :param indent: indent
        :return: sql statements after format
        """
        return super(Sql, self).format(indent)

    def tokens(self):
        """
        return tokens of Statements
        """
        return super(Sql, self).tokens()

