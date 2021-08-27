from __future__ import annotations

import abc
from abc import ABC
from typing import Union

from z64c.ast import (
    Program,
    Print,
    Assignment,
    Addition,
    Negation,
    Identifier,
    Unsignedint,
)
from z64c.ast import AstVisitor
from z64c.types import Type


class Environment:
    def __init__(self):
        self._variable_types = {}

    def add_variable(self, name: str, variable_type: Type):
        self._variable_types[name] = variable_type

    def get_variable_type(self, name: str) -> Union[Type, TypecheckError]:
        return self._variable_types.get(name, UndefinedVariable(name))


class TypecheckError(ABC):
    @abc.abstractmethod
    def make_error_message(self) -> str:
        pass

    def __eq__(self, rhs: TypecheckError):
        return self.make_error_message() == rhs.make_error_message()


class CombinedTypecheckErrors(TypecheckError):
    def __init__(self, errors: [TypecheckError]):
        self._errors = errors

    def make_error_message(self) -> str:
        return "".join(
            [error.make_error_message() + "\n" for error in self._errors]
        ).rstrip("\n")


class TypeMismatch(TypecheckError):
    def __init__(self, expected_type: Type, received_type: Type):
        self._expected_type = expected_type
        self._received_type = received_type

    def make_error_message(self) -> str:
        return (
            f"Expected type {self._expected_type}. Received type {self._received_type}."
        )


class UndefinedVariable(TypecheckError):
    def __init__(self, variable_name: str):
        self._variable_name = variable_name

    def make_error_message(self) -> str:
        return f"Undefined variable {self._variable_name}."


TypecheckResult = Union[Type, TypecheckError]


class TypecheckerVisitor(AstVisitor[TypecheckResult]):
    def __init__(self, environment: Environment = Environment()):
        self._environment = environment

    def visitProgram(self, node: Program) -> TypecheckResult:
        checks: TypecheckResult = []
        for statement in node._statements:
            checks.append(statement.visit(self))

        errors = [error for error in checks if isinstance(error, TypecheckError)]
        if errors:
            return CombinedTypecheckErrors(errors)

        return Type.VOID

    def visitPrint(self, node: Print) -> TypecheckResult:
        check_result = node._expression.visit(self)
        if isinstance(check_result, TypecheckError):
            return check_result

        return Type.VOID

    def visitAssigment(self, node: Assignment) -> TypecheckResult:
        self._environment.add_variable(node._name, Type.U8)
        return Type.VOID

    def visitAddition(self, node: Addition) -> TypecheckResult:
        lhs_check_result = node._lhs.visit(self)
        rhs_check_result = node._rhs.visit(self)

        if isinstance(lhs_check_result, TypecheckError):
            return lhs_check_result

        if isinstance(rhs_check_result, TypecheckError):
            return rhs_check_result

        if lhs_check_result is not Type.U8:
            return TypeMismatch(Type.U8, lhs_check_result)

        if rhs_check_result is not Type.U8:
            return TypeMismatch(Type.U8, rhs_check_result)

        return Type.U8

    def visitNegation(self, node: Negation) -> TypecheckResult:
        check_result = node._expression.visit(self)

        if isinstance(check_result, TypecheckError):
            return check_result

        if check_result is not Type.U8:
            return TypeMismatch(Type.U8, check_result)

        return check_result

    def visitIdentifier(self, node: Identifier) -> TypecheckResult:
        return self._environment.get_variable_type(node._value)

    def visitUnsignedint(self, node: Unsignedint) -> TypecheckResult:
        return Type.U8
