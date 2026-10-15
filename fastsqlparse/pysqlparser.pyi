from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

class DIALECT:
    # Dialect selector used by the parser binding.
    # Members mirror fastsqlparse.conf.DialectType (DialectType = pysqlparser.DIALECT).
    ANSI: "DIALECT"
    MYSQL: "DIALECT"
    PGSQL: "DIALECT"
    SQLITE: "DIALECT"
    DORIS: "DIALECT"

# Convenience aliases re-exported by fastsqlparse.conf
DIALECT_ANSI: DIALECT
DIALECT_MYSQL: DIALECT
DIALECT_POSTGRESQL: DIALECT
DIALECT_SQLITE: DIALECT
DIALECT_DORIS: DIALECT

class Token:
    type: str
    value: str
    at: int

class DqlSourceExpr:
    # A FROM-level source: .raw is the full source expression text as written.
    table: str
    alias: str
    database: str
    raw: str

class DqlColumnExpr:
    # Column expression from the SELECT list. NOTE: the column name attribute
    # is `field` (not `name`); `alias` is the AS-alias (empty when absent).
    field: str
    table: str
    alias: str

class DqlClause:
    part: str
    clause: str

class QueryStatement:
    # Normal SELECT form exposes sources/columns/clauses/subquery.
    # UNION form typically exposes T == "UNIONS" and the `unions` list.
    T: str
    sources: List[DqlSourceExpr]
    columns: List[DqlColumnExpr]
    clauses: List[DqlClause]
    clause_select: List[str]
    subquery: Dict[str, Any]
    unions: List[Any]

class CommonTableExpr:
    common_tables: List[str]
    expressions: Dict[str, Any]

class ParsedWithStmt:
    units: List[Any]

class AbstractStatement:
    @classmethod
    def tokenize(cls, statement: str, dialect: DIALECT = DIALECT_ANSI) -> List[Tuple[str, str, int]]: ...

class Dql(AbstractStatement): ...
class Insert(AbstractStatement): ...
class Update(AbstractStatement): ...
class Delete(AbstractStatement): ...
class View(AbstractStatement): ...
class Create(AbstractStatement): ...
class WithStatement(AbstractStatement): ...

class ParsedCTE:
    # Accepts a WITH-clause fragment ("WITH a AS (...), b AS (...)"), NOT a full
    # statement ("WITH ... SELECT ..."): pass full statements to ParsedQuery.
    # Per-CTE names live on the ParsedCTE objects inside `units` (unit.name),
    # not on this wrapper.
    raw: str
    units: List[Any]
    def format(self, indent: str = ..., init_indent: int = ...) -> str: ...
    def ast(self) -> str: ...
    def tokens(self) -> List[Any]: ...
    @classmethod
    def tokenize(cls, statement: str, dialect: DIALECT = DIALECT_ANSI) -> List[Tuple[str, str, int]]: ...

class ParsedInsert:
    raw: str
    name: str
    query_load: bool
    cte: Optional[ParsedWithStmt]
    query: Any
    columns: List[str]
    values: List[str]
    main_stmt: str
    cte_stmt: str
    query_stmt: str
    def format(self, indent: str = ..., init_indent: int = ...) -> str: ...
    def ast(self) -> str: ...
    def tokens(self) -> List[Any]: ...
    @classmethod
    def tokenize(cls, statement: str, dialect: DIALECT = DIALECT_ANSI) -> List[Tuple[str, str, int]]: ...

class ParsedQuery:
    name: str
    raw: str
    super: str
    parent: Any
    level: int
    parsed: Any
    cte: Optional[CommonTableExpr]
    statement: str
    def format(self, indent: str = ..., init_indent: int = ...) -> str: ...
    def ast(self) -> str: ...
    def tokens(self) -> List[Any]: ...
    def available_cte(self) -> Dict[str, ParsedCTE]: ...
    @classmethod
    def tokenize(cls, statement: str, dialect: DIALECT = DIALECT_ANSI) -> List[Tuple[str, str, int]]: ...
    @staticmethod
    def parse_dependence(statement: str, dialect: str = "ansi") -> List[str]: ...

class ParsedView:
    raw: str
    name: str
    query: Any
    def format(self, indent: str = ..., init_indent: int = ...) -> str: ...
    def ast(self) -> str: ...
    def tokens(self) -> List[Any]: ...
    @classmethod
    def tokenize(cls, statement: str, dialect: DIALECT = DIALECT_ANSI) -> List[Tuple[str, str, int]]: ...

class ParsedUpdate:
    name: str
    raw: str
    condition: Any
    fields: List[Any]
    values: List[Any]
    def tokens(self) -> List[Any]: ...
    @classmethod
    def tokenize(cls, statement: str, dialect: DIALECT = DIALECT_ANSI) -> List[Tuple[str, str, int]]: ...

class ParsedDelete:
    name: str
    raw: str
    condition: Any
    def tokens(self) -> List[Any]: ...
    @classmethod
    def tokenize(cls, statement: str, dialect: DIALECT = DIALECT_ANSI) -> List[Tuple[str, str, int]]: ...

class ParsedCreate:
    name: str
    raw: str
    comment: Any
    pri_key: Any
    columns: List[Any]
    def ast(self) -> str: ...
    def tokens(self) -> List[Any]: ...
    @classmethod
    def tokenize(cls, statement: str, dialect: DIALECT = DIALECT_ANSI) -> List[Tuple[str, str, int]]: ...

class ParsedOne:
    parsed: Any
    type: str
    def AST(self) -> str: ...
    def ast(self) -> Any: ...
    def format(self, indent: str = ...) -> str: ...
    def tokens(self) -> List[Any]: ...

class Parsed:
    parsed_forest: List[Any]
    statements: List[str]
    name: str
    def content(self) -> str: ...
    def AST(self) -> str: ...
    def ast(self) -> Any: ...
    def format(self, indent: str = ...) -> str: ...
    def tokens(self) -> List[Any]: ...

# top-level convenience functions exposed by the package

def format(sql: str, s_type: str, indent: str = ..., dialect: str = "ansi") -> str:
    """
    Format a single SQL statement.

    `s_type` is required and selects the statement type:
    "query" | "insert" | "update" | "delete" | "create" | "cte" | "view".
    Unknown types raise RuntimeError.
    """
    ...

def strip_comments(statement: str, dialect: str = "ansi") -> str: ...

def tokenize(statement: str, dialect: DIALECT = DIALECT_ANSI) -> List[Tuple[str, str, int]]: ...

def query(statement: str, name: str, pure: bool = ..., dialect: str = "ansi") -> Any: ...
def insert(statement: str, pure: bool = ..., dialect: str = "ansi") -> Any: ...
def update(statement: str, pure: bool = ..., dialect: str = "ansi") -> Any: ...
def delete(statement: str, pure: bool = ..., dialect: str = "ansi") -> Any: ...
def view(statement: str, pure: bool = ..., dialect: str = "ansi") -> Any: ...
def cte(statement: str, pure: bool = ..., dialect: str = "ansi") -> Any: ...
def create(statement: str, pure: bool = ..., dialect: str = "ansi") -> Any: ...
def parse_dependence(statement: str, dialect: str = "ansi") -> List[str]: ...

