from __future__ import annotations

import abc
from abc import ABC

from zx64c.parser import SourceContext
from zx64c.types import Type


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


class TypeMismatchError(TypecheckError):
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


class NoReturnError(TypecheckError):
    def __init__(self, expected_type: Type, function_name: str, context: SourceContext):
        super().__init__(context)
        self._expected_type = expected_type
        self._function_name = function_name

    def _make_error_message(self) -> str:
        return (
            f"Function `{self._function_name} return type is "
            f"{self._expected_type}, but there is no return statement inside it."
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


class UndefinedVariableError(TypecheckError):
    def __init__(self, variable_name: str, context: SourceContext):
        super().__init__(context)
        self._variable_name = variable_name

    def _make_error_message(self) -> str:
        return f"Undefined variable {self._variable_name}."
