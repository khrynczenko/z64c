from __future__ import annotations

import abc
from abc import ABC

from zx64c.ast import (
    SourceContext,
    Program,
    Block,
    If,
    Print,
    Let,
    Assignment,
    Addition,
    Negation,
    Identifier,
    Unsignedint,
    Bool,
)
from zx64c.ast import AstVisitor
from zx64c.types import Type, VOID, U8, BOOL


class Environment:
    def __init__(self):
        self._variable_types = {}
        self._defined_types = [VOID, U8, BOOL]

    def add_type(self, udt: Type):
        self._defined_types.append(udt)

    def add_variable(self, name: str, var_type: Type, context: SourceContext):
        if var_type not in self._defined_types:
            raise UndefinedTypeError(var_type, context)

        self._variable_types[name] = var_type

    def has_variable(self, name):
        return name in self._variable_types

    def get_variable_type(self, name: str, context: SourceContext) -> Type:
        """
        :param context: used to create error in case the variable is not defined
        """
        try:
            return self._variable_types[name]
        except KeyError:
            raise UndefinedVariable(name, context)


class TypecheckError(Exception, ABC):
    def __init__(self, context: SourceContext):
        self._context = context

    def make_error_message(self) -> str:
        return (
            f"At line {self._context.line}, column {self._context.column}: "
            f"{self._make_error_message()}"
        )

    @abc.abstractmethod
    def _make_error_message(self) -> str:
        pass

    def __eq__(self, rhs: TypecheckError):
        return self.make_error_message() == rhs.make_error_message()


class CombinedTypecheckError(TypecheckError):
    def __init__(self, errors: [TypecheckError]):
        self._errors = errors

    def make_error_message(self) -> str:
        return "".join(
            [error.make_error_message() + "\n" for error in self._errors]
        ).rstrip("\n")


class TypeMismatch(TypecheckError):
    def __init__(
        self, expected_type: Type, received_type: Type, context: SourceContext
    ):
        super().__init__(context)
        self._expected_type = expected_type
        self._received_type = received_type

    def _make_error_message(self) -> str:
        return (
            f"Expected type {self._expected_type}. Received type {self._received_type}."
        )


class AlreadyDefinedVariableError(TypecheckError):
    def __init__(self, var_name: str, context: SourceContext):
        super().__init__(context)
        self._var_name = var_name

    def _make_error_message(self) -> str:
        return f"Variable `{self._var_name}` is already defined."


class UndefinedTypeError(TypecheckError):
    def __init__(self, var_type: Type, context: SourceContext):
        super().__init__(context)
        self._var_type = var_type

    def _make_error_message(self) -> str:
        return f"Undefined type {self._var_type}."


class UndefinedVariable(TypecheckError):
    def __init__(self, variable_name: str, context: SourceContext):
        super().__init__(context)
        self._variable_name = variable_name

    def _make_error_message(self) -> str:
        return f"Undefined variable {self._variable_name}."


class TypecheckerVisitor(AstVisitor[Type]):
    def __init__(self, environment: Environment = None):
        if environment is None:
            environment = Environment()
        self._environment = environment

    def visit_program(self, node: Program) -> Type:
        type_errors: [TypecheckError] = []
        for statement in node.statements:
            try:
                statement.visit(self)
            except TypecheckError as e:
                type_errors.append(e)

        if type_errors:
            raise CombinedTypecheckError(type_errors)

        return VOID

    def visit_block(self, node: Block) -> Type:
        type_errors: [TypecheckError] = []
        for statement in node.statements:
            try:
                statement.visit(self)
            except TypecheckError as e:
                type_errors.append(e)

        if type_errors:
            raise CombinedTypecheckError(type_errors)

        return VOID

    def visit_if(self, node: If) -> Type:
        condition_type = node.condition.visit(self)
        if condition_type != BOOL:
            raise TypeMismatch(BOOL, condition_type, node.condition.context)

        node.consequence.visit(self)

        return VOID

    def visit_print(self, node: Print) -> Type:
        node.expression.visit(self)

        return VOID

    def visit_let(self, node: Let) -> Type:
        rhs_type = node.rhs.visit(self)

        if self._environment.has_variable(node.name):
            raise AlreadyDefinedVariableError(node.name, node.context)

        self._environment.add_variable(node.name, node.var_type, node.context)

        variable_type = self._environment.get_variable_type(node.name, node.context)
        if variable_type != rhs_type:
            raise TypeMismatch(variable_type, rhs_type, node.context)

        return VOID

    def visit_assignment(self, node: Assignment) -> Type:
        rhs_type = node.rhs.visit(self)

        variable_type = self._environment.get_variable_type(node.name, node.context)
        if variable_type != rhs_type:
            raise TypeMismatch(variable_type, rhs_type, node.context)

        return VOID

    def visit_addition(self, node: Addition) -> Type:
        lhs_type = node.lhs.visit(self)
        rhs_type = node.rhs.visit(self)

        if lhs_type != U8:
            raise TypeMismatch(U8, lhs_type, node.lhs.context)

        if rhs_type != U8:
            raise TypeMismatch(U8, rhs_type, node.rhs.context)

        return U8

    def visit_negation(self, node: Negation) -> Type:
        expression_type = node.expression.visit(self)

        if expression_type != U8:
            raise TypeMismatch(U8, expression_type, node.context)

        return expression_type

    def visit_identifier(self, node: Identifier) -> Type:
        return self._environment.get_variable_type(node.value, node.context)

    def visit_unsignedint(self, node: Unsignedint) -> Type:
        return U8

    def visit_bool(self, node: Bool) -> Type:
        return BOOL
