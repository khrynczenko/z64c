from __future__ import annotations

import abc

from typing import List, Text, TypeVar, Generic
from abc import ABC

T = TypeVar("T")


class AstVisitor(ABC, Generic[T]):
    def visitProgram(self, node: Program) -> T:
        pass

    def visitPrint(self, node: Print) -> T:
        pass

    def visitAssigment(self, node: Assignment) -> T:
        pass

    def visitAddition(self, node: Addition) -> T:
        pass

    def visitNegation(self, node: Negation) -> T:
        pass

    def visitIdentifier(self, node: Identifier) -> T:
        pass

    def visitUnsignedint(self, node: Unsignedint) -> T:
        pass


class Ast(ABC):
    @abc.abstractmethod
    def visit(self, v: AstVisitor[T]) -> T:
        pass


class SjasmplusSnapshotProgram(Ast):
    def __init__(self, program: Program, source_name: Text):
        self._program = program
        self._source_name = source_name

    def __eq__(self, rhs: SjasmplusSnapshotProgram) -> bool:
        return self._program == rhs._program and self._source_name == rhs._source_name

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitProgram(self)


class Program(Ast):
    def __init__(self, statements: List[Ast]):
        self._statements = statements

    def __eq__(self, rhs: Program) -> bool:
        return self._statements == rhs._statements

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitProgram(self)


class Print(Ast):
    def __init__(self, expression: Ast):
        self._expression = expression

    def __eq__(self, rhs: Print) -> bool:
        return self._expression == rhs._expression

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitPrint(self)


class Assignment(Ast):
    def __init__(self, name: str, rhs: Ast):
        self._name = name
        self._rhs = rhs

    def __eq__(self, rhs: Assignment) -> bool:
        return self._name == rhs._name and self._rhs == rhs._rhs

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitAssigment(self)


class Addition(Ast):
    def __init__(self, lhs: Ast, rhs: Ast):
        self._lhs = lhs
        self._rhs = rhs

    def __eq__(self, rhs: Addition) -> bool:
        return self._lhs == rhs._lhs and self._rhs == rhs._rhs

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitAddition(self)


class Negation(Ast):
    def __init__(self, expression: Ast):
        self._expression = expression

    def __eq__(self, rhs: Negation) -> bool:
        return self._expression == rhs._expression

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitNegation(self)


class Identifier(Ast):
    def __init__(self, value: str):
        self._value = value

    def __eq__(self, rhs: Identifier) -> bool:
        return self._value == rhs._value

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitIdentifier(self)


class Unsignedint(Ast):
    def __init__(self, value: int):
        self._value = value

    def __eq__(self, rhs: Unsignedint) -> bool:
        return self._value == rhs._value

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitUnsignedint(self)
