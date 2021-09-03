from __future__ import annotations

import abc

from typing import List, Text, TypeVar, Generic
from abc import ABC

T = TypeVar("T")


class AstVisitor(ABC, Generic[T]):
    def visit_program(self, node: Program) -> T:
        pass

    def visit_block(self, node: Block) -> T:
        pass

    def visit_if(self, node: Block) -> T:
        pass

    def visit_print(self, node: Print) -> T:
        pass

    def visit_assignment(self, node: Assignment) -> T:
        pass

    def visit_addition(self, node: Addition) -> T:
        pass

    def visit_negation(self, node: Negation) -> T:
        pass

    def visit_identifier(self, node: Identifier) -> T:
        pass

    def visit_unsignedint(self, node: Unsignedint) -> T:
        pass

    def visit_bool(self, node: Bool) -> T:
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
        self.program = program
        self.source_name = source_name

    def __eq__(self, rhs: SjasmplusSnapshotProgram) -> bool:
        return self.program == rhs.program and self.source_name == rhs._source_name

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_program(self)


class Program(Ast):
    def __init__(self, statements: List[Ast], context: SourceContext):
        super().__init__(context)
        self.statements = statements

    def __eq__(self, rhs: Program) -> bool:
        return self.statements == rhs.statements and self.context == rhs.context

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_program(self)


class Block(Ast):
    def __init__(self, statements: [Ast], context: SourceContext):
        super().__init__(context)
        self.statements = statements

    def __eq__(self, rhs: If) -> bool:
        return self.statements == rhs.statements

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_block(self)


class If(Ast):
    def __init__(self, condition: Ast, consequence: Ast, context: SourceContext):
        super().__init__(context)
        self.condition = condition
        self.consequence = consequence

    def __eq__(self, rhs: If) -> bool:
        return self.condition == rhs.condition and self.consequence == rhs.consequence

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_if(self)


class Print(Ast):
    def __init__(self, expression: Ast, context: SourceContext):
        super().__init__(context)
        self.expression = expression

    def __eq__(self, rhs: Print) -> bool:
        return self.expression == rhs.expression and self.context == rhs.context

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_print(self)


class Assignment(Ast):
    def __init__(self, name: str, rhs: Ast, context: SourceContext):
        super().__init__(context)
        self.name = name
        self.rhs = rhs

    def __eq__(self, rhs: Assignment) -> bool:
        return (
            self.name == rhs.name
            and self.rhs == rhs.rhs
            and self.context == rhs.context
        )

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_assignment(self)


class Addition(Ast):
    def __init__(self, lhs: Ast, rhs: Ast, context: SourceContext):
        super().__init__(context)
        self.lhs = lhs
        self.rhs = rhs

    def __eq__(self, rhs: Addition) -> bool:
        return (
            self.lhs == rhs.lhs and self.rhs == rhs.rhs and self.context == rhs.context
        )

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_addition(self)


class Negation(Ast):
    def __init__(self, expression: Ast, context: SourceContext):
        super().__init__(context)
        self.expression = expression

    def __eq__(self, rhs: Negation) -> bool:
        return self.expression == rhs.expression and self.context == rhs.context

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_negation(self)


class Identifier(Ast):
    def __init__(self, value: int, context: SourceContext):
        super().__init__(context)
        self.value = value

    def __eq__(self, rhs: Identifier) -> bool:
        return self.value == rhs.value and self.context == self.context

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_identifier(self)


class Unsignedint(Ast):
    def __init__(self, value: int, context: SourceContext):
        super().__init__(context)
        self.value = value

    def __eq__(self, rhs: Unsignedint) -> bool:
        return self.value == rhs.value and self.context == self.context

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_unsignedint(self)


class Bool(Ast):
    def __init__(self, value: bool, context: SourceContext):
        super().__init__(context)
        self.value = value

    def __eq__(self, rhs: Unsignedint) -> bool:
        return self.value == rhs.value and self.context == self.context

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_bool(self)
