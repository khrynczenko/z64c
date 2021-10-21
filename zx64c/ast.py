from __future__ import annotations

import abc

from typing import List, Text, TypeVar, Generic
from abc import ABC
from functools import singledispatchmethod
from dataclasses import dataclass

from zx64c.types import Type, Callable

T = TypeVar("T")


class AstVisitor(ABC, Generic[T]):
    @abc.abstractmethod
    def visit_program(self, node: Program) -> T:
        pass

    @abc.abstractmethod
    def visit_function(self, node: Function) -> T:
        pass

    @abc.abstractmethod
    def visit_block(self, node: Block) -> T:
        pass

    @abc.abstractmethod
    def visit_if(self, node: Block) -> T:
        pass

    @abc.abstractmethod
    def visit_print(self, node: Print) -> T:
        pass

    @abc.abstractmethod
    def visit_let(self, node: Assignment) -> T:
        pass

    @abc.abstractmethod
    def visit_return(self, node: Return) -> T:
        pass

    @abc.abstractmethod
    def visit_assignment(self, node: Assignment) -> T:
        pass

    @abc.abstractmethod
    def visit_equal(self, node: Equal) -> T:
        pass

    @abc.abstractmethod
    def visit_not_equal(self, node: NotEqual) -> T:
        pass

    @abc.abstractmethod
    def visit_addition(self, node: Addition) -> T:
        pass

    @abc.abstractmethod
    def visit_subtraction(self, node: Subtraction) -> T:
        pass

    @abc.abstractmethod
    def visit_negation(self, node: Negation) -> T:
        pass

    @abc.abstractmethod
    def visit_function_call(self, node: FunctionCall) -> T:
        pass

    @abc.abstractmethod
    def visit_identifier(self, node: Identifier) -> T:
        pass

    @abc.abstractmethod
    def visit_unsignedint(self, node: Unsignedint) -> T:
        pass

    @abc.abstractmethod
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

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_program(self)


@SjasmplusSnapshotProgram.__eq__.register
def __eq__(self, rhs: SjasmplusSnapshotProgram) -> bool:
    return self.program == rhs.program and self.source_name == rhs._source_name


class Program(Ast):
    def __init__(self, functions: List[Function], context: SourceContext):
        super().__init__(context)
        self.functions = functions

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_program(self)


@Program.__eq__.register
def _(self, rhs: Program) -> bool:
    return self.functions == rhs.functions and self.context == rhs.context


@dataclass
class Parameter:
    name: str
    type_id: Type


class Function(Ast):
    def __init__(
        self,
        name: str,
        parameters: List[Parameter],
        return_type: Type,
        code_block: Block,
        context: SourceContext,
    ):
        super().__init__(context)
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.code_block = code_block
        self.type = Callable(return_type, [p.type_id for p in parameters])

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_function(self)


@Function.__eq__.register
def _(self, rhs: Function) -> bool:
    return (
        self.name == rhs.name
        and self.parameters == rhs.parameters
        and self.return_type == rhs.return_type
        and self.code_block == rhs.code_block
    )


class Block(Ast):
    def __init__(self, statements: [Ast], context: SourceContext):
        super().__init__(context)
        self.statements = statements

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_block(self)


@Block.__eq__.register
def _(self, rhs: Block) -> bool:
    return self.statements == rhs.statements


class If(Ast):
    def __init__(self, condition: Ast, consequence: Ast, context: SourceContext):
        super().__init__(context)
        self.condition = condition
        self.consequence = consequence

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_if(self)


@If.__eq__.register
def _(self, rhs: If) -> bool:
    return self.condition == rhs.condition and self.consequence == rhs.consequence


class Print(Ast):
    def __init__(self, expression: Ast, context: SourceContext):
        super().__init__(context)
        self.expression = expression

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_print(self)


@Print.__eq__.register
def _(self, rhs: Print) -> bool:
    return self.expression == rhs.expression and self.context == rhs.context


class Let(Ast):
    def __init__(self, name: str, var_type: Type, rhs: Ast, context: SourceContext):
        super().__init__(context)
        self.name = name
        self.var_type = var_type
        self.rhs = rhs

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_let(self)


@Let.__eq__.register
def _(self, rhs: Let) -> bool:
    return (
        self.name == rhs.name
        and self.var_type == rhs.var_type
        and self.rhs == rhs.rhs
        and self.context == rhs.context
    )


class Assignment(Ast):
    def __init__(self, name: str, rhs: Ast, context: SourceContext):
        super().__init__(context)
        self.name = name
        self.rhs = rhs

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_assignment(self)


@Assignment.__eq__.register
def _(self, rhs: Assignment) -> bool:
    return self.name == rhs.name and self.rhs == rhs.rhs and self.context == rhs.context


class Return(Ast):
    def __init__(self, expr: Ast, context: SourceContext):
        super().__init__(context)
        self.expr = expr

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_return(self)


@Return.__eq__.register
def _(self, rhs: Return) -> bool:
    return self.expr == rhs.expr


class Equal(Ast):
    def __init__(self, lhs: Ast, rhs: Ast, context: SourceContext):
        super().__init__(context)
        self.lhs = lhs
        self.rhs = rhs

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_equal(self)


@Equal.__eq__.register
def _(self, rhs: Equal) -> bool:
    return self.lhs == rhs.lhs and self.rhs == rhs.rhs and self.context == rhs.context


class NotEqual(Ast):
    def __init__(self, lhs: Ast, rhs: Ast, context: SourceContext):
        super().__init__(context)
        self.lhs = lhs
        self.rhs = rhs

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_not_equal(self)


@NotEqual.__eq__.register
def _(self, rhs: NotEqual) -> bool:
    return self.lhs == rhs.lhs and self.rhs == rhs.rhs and self.context == rhs.context


class Addition(Ast):
    def __init__(self, lhs: Ast, rhs: Ast, context: SourceContext):
        super().__init__(context)
        self.lhs = lhs
        self.rhs = rhs

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_addition(self)


@Addition.__eq__.register
def _(self, rhs: Addition) -> bool:
    return self.lhs == rhs.lhs and self.rhs == rhs.rhs and self.context == rhs.context


class Subtraction(Ast):
    def __init__(self, lhs: Ast, rhs: Ast, context: SourceContext):
        super().__init__(context)
        self.lhs = lhs
        self.rhs = rhs

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_subtraction(self)


@Subtraction.__eq__.register
def _(self, rhs: Subtraction) -> bool:
    return self.lhs == rhs.lhs and self.rhs == rhs.rhs and self.context == rhs.context


class Negation(Ast):
    def __init__(self, expression: Ast, context: SourceContext):
        super().__init__(context)
        self.expression = expression

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_negation(self)


@Negation.__eq__.register
def _(self, rhs: Negation) -> bool:
    return self.expression == rhs.expression and self.context == rhs.context


class FunctionCall(Ast):
    def __init__(
        self, function_name: str, arguments: List[Ast], context: SourceContext
    ):
        super().__init__(context)
        self.function_name = function_name
        self.arguments = arguments

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_function_call(self)


@FunctionCall.__eq__.register
def _(self, rhs: FunctionCall) -> bool:
    return (
        self.function_name == rhs.function_name
        and self.arguments == rhs.arguments
        and self.context == rhs.context
    )


class Identifier(Ast):
    def __init__(self, value: int, context: SourceContext):
        super().__init__(context)
        self.value = value

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_identifier(self)


@Identifier.__eq__.register
def _(self, rhs: Identifier) -> bool:
    return (
        isinstance(rhs, Identifier)
        and self.value == rhs.value
        and self.context == self.context
    )


class Unsignedint(Ast):
    def __init__(self, value: int, context: SourceContext):
        super().__init__(context)
        self.value = value

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_unsignedint(self)


@Unsignedint.__eq__.register
def _(self, rhs: Unsignedint) -> bool:
    return (
        isinstance(rhs, Unsignedint)
        and self.value == rhs.value
        and self.context == self.context
    )


class Bool(Ast):
    def __init__(self, value: bool, context: SourceContext):
        super().__init__(context)
        self.value = value

    @singledispatchmethod
    def __eq__(self, rhs: Ast) -> bool:
        return False

    def visit(self, v: AstVisitor[T]) -> T:
        return v.visit_bool(self)


@Bool.__eq__.register
def _(self, rhs: Bool) -> bool:
    return (
        isinstance(rhs, Bool)
        and self.value == rhs.value
        and self.context == self.context
    )
