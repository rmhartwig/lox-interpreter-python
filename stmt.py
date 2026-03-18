# Defines all statement AST node types and the visitor interface.
# Statements represent executable units like print, var, if, while, etc.
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from expr import Expr, Variable
from lox_token import Token


class StmtVisitor(ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt: "Expression") -> Any:
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: "Print") -> Any:
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: "Var") -> Any:
        pass

    @abstractmethod
    def visit_block_stmt(self, stmt: "Block") -> Any:
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: "If") -> Any:
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: "While") -> Any:
        pass

    @abstractmethod
    def visit_function_stmt(self, stmt: "Function") -> Any:
        pass

    @abstractmethod
    def visit_return_stmt(self, stmt: "Return") -> Any:
        pass

    @abstractmethod
    def visit_class_stmt(self, stmt: "Class") -> Any:
        pass


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor) -> Any:
        pass


@dataclass(frozen=True)
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_expression_stmt(self)


@dataclass(frozen=True)
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_print_stmt(self)


@dataclass(frozen=True)
class Var(Stmt):
    name: Token
    initializer: Expr | None

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_var_stmt(self)


@dataclass(frozen=True)
class Block(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_block_stmt(self)


@dataclass(frozen=True)
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_if_stmt(self)


@dataclass(frozen=True)
class While(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_while_stmt(self)


@dataclass(frozen=True)
class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_function_stmt(self)


@dataclass(frozen=True)
class Return(Stmt):
    keyword: Token
    value: Expr | None

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_return_stmt(self)


@dataclass(frozen=True)
class Class(Stmt):
    name: Token
    superclass: Variable | None
    methods: list[Function]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_class_stmt(self)