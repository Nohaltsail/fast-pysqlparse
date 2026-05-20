from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

class Token:
    type: str
    value: str
    at: int

class DqlSourceExpr:
    table: str
    alias: str

class DqlColumnExpr:
    name: str
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
    def tokenize(cls, statement: str) -> List[Tuple[str, str, int]]: ...

class Dql(AbstractStatement): ...
class Insert(AbstractStatement): ...
class Update(AbstractStatement): ...
class Delete(AbstractStatement): ...
class View(AbstractStatement): ...
class WithStatement(AbstractStatement): ...

class ParsedCTE:
    raw: str
    units: List[Any]
    name: Optional[str]
    def format(self, indent: str = ..., init_indent: int = ...) -> str: ...
    def ast(self) -> str: ...
    def tokens(self) -> List[Any]: ...
    @classmethod
    def tokenize(cls, statement: str) -> List[Tuple[str, str, int]]: ...

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
    def tokenize(cls, statement: str) -> List[Tuple[str, str, int]]: ...

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
    def tokenize(cls, statement: str) -> List[Tuple[str, str, int]]: ...
    @staticmethod
    def parse_dependence(statement: str) -> List[str]: ...

class ParsedView:
    raw: str
    name: str
    query: Any
    def format(self, indent: str = ..., init_indent: int = ...) -> str: ...
    def ast(self) -> str: ...
    def tokens(self) -> List[Any]: ...
    @classmethod
    def tokenize(cls, statement: str) -> List[Tuple[str, str, int]]: ...

class ParsedUpdate:
    name: str
    raw: str
    condition: Any
    fields: List[Any]
    values: List[Any]
    def tokens(self) -> List[Any]: ...
    @classmethod
    def tokenize(cls, statement: str) -> List[Tuple[str, str, int]]: ...

class ParsedDelete:
    name: str
    raw: str
    condition: Any
    def tokens(self) -> List[Any]: ...
    @classmethod
    def tokenize(cls, statement: str) -> List[Tuple[str, str, int]]: ...

class ParsedCreate:
    name: str
    raw: str
    comment: Any
    pri_key: Any
    columns: List[Any]
    def ast(self) -> str: ...

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
format: Any
strip_comments: Any

def query(statement: str, name: str, pure: bool = ...) -> Any: ...
def insert(statement: str, pure: bool = ...) -> Any: ...
def update(statement: str) -> Any: ...
def delete(statement: str) -> Any: ...
def view(statement: str, pure: bool = ...) -> Any: ...
def cte(statement: str, pure: bool = ...) -> Any: ...
def create(statement: str) -> Any: ...
def parse_dependence(statement: str) -> List[str]: ...

