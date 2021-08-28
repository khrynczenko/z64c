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


class SourceContext:
    def __init__(self, line: int, column: int):
        self._line = line
        self._column = column

    def __eq__(self, rhs: SourceContext) -> bool:
        return self._line == rhs._line and self._column == rhs._column

    @property
    def line(self) -> int:
        return self._line

    @property
    def column(self) -> int:
        return self._column


class Ast(ABC):
    def __init__(self, context: SourceContext):
        self._context = context

    @property
    def context(self) -> SourceContext:
        return self._context

    @abc.abstractmethod
    def visit(self, v: AstVisitor[T]) -> T:
        pass

    @abc.abstractmethod
    def __eq__(self, rhs: Ast) -> bool:
        pass


class SjasmplusSnapshotProgram(Ast):
    def __init__(self, program: Program, source_name: Text):
        super().__init__(program.context)
        self._program = program
        self._source_name = source_name

    def __eq__(self, rhs: SjasmplusSnapshotProgram) -> bool:
        return self._program == rhs._program and self._source_name == rhs._source_name

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitProgram(self)


class Program(Ast):
    def __init__(self, statements: List[Ast], context: SourceContext):
        super().__init__(context)
        self._statements = statements

    def __eq__(self, rhs: Program) -> bool:
        return self._statements == rhs._statements and self.context == rhs.context

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitProgram(self)


class Print(Ast):
    def __init__(self, expression: Ast, context: SourceContext):
        super().__init__(context)
        self._expression = expression

    def __eq__(self, rhs: Print) -> bool:
        return self._expression == rhs._expression and self.context == rhs.context

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitPrint(self)


class Assignment(Ast):
    def __init__(self, name: str, rhs: Ast, context: SourceContext):
        super().__init__(context)
        self._name = name
        self._rhs = rhs

    def __eq__(self, rhs: Assignment) -> bool:
        return (
            self._name == rhs._name
            and self._rhs == rhs._rhs
            and self.context == rhs.context
        )

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitAssigment(self)


class Addition(Ast):
    def __init__(self, lhs: Ast, rhs: Ast, context: SourceContext):
        super().__init__(context)
        self._lhs = lhs
        self._rhs = rhs

    def __eq__(self, rhs: Addition) -> bool:
        return (
            self._lhs == rhs._lhs
            and self._rhs == rhs._rhs
            and self.context == rhs.context
        )

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitAddition(self)


class Negation(Ast):
    def __init__(self, expression: Ast, context: SourceContext):
        super().__init__(context)
        self._expression = expression

    def __eq__(self, rhs: Negation) -> bool:
        return self._expression == rhs._expression and self.context == rhs.context

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitNegation(self)


class Identifier(Ast):
    def __init__(self, value: int, context: SourceContext):
        super().__init__(context)
        self._value = value

    def __eq__(self, rhs: Identifier) -> bool:
        return self._value == rhs._value and self.context == self.context

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitIdentifier(self)


class Unsignedint(Ast):
    def __init__(self, value: int, context: SourceContext):
        super().__init__(context)
        self._value = value

    def __eq__(self, rhs: Unsignedint) -> bool:
        return self._value == rhs._value and self.context == self.context

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visitUnsignedint(self)
