from __future__ import annotations

import abc
from abc import ABC


class Type(ABC):
    @abc.abstractmethod
    def __eq__(self, rhs: Type):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    @staticmethod
    def is_numerical() -> bool:
        return False

    # We are using double dispatch here (1st dispatch)
    def infer(self, to: Type) -> Type:
        """
        Usually this methods just returns `self` but for a number literal
        this would infer what kind od number it needs to be by dispatching
        to the method `infer_from_number_literal` and passing self to it.
        """
        return self

    # 2nd dispatch
    def infer_from_number_literal(self, literal: Type) -> Type:
        return literal


class TypeIdentifier(Type):
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, rhs: Type):
        return isinstance(rhs, TypeIdentifier) and self.name == rhs.name

    def __str__(self):
        return self.name


class Void(Type):
    def __eq__(self, rhs: Type):
        return isinstance(rhs, Void)

    def __str__(self):
        return "void"


class Numerical(Type, ABC):
    @staticmethod
    @abc.abstractmethod
    def is_signed() -> bool:
        pass

    @staticmethod
    def is_numerical() -> bool:
        return True


class U8(Numerical):
    def is_signed() -> bool:
        return False

    def __eq__(self, rhs: Type):
        return isinstance(rhs, U8)

    def __str__(self):
        return "u8"

    def infer_from_number_literal(self, literal: Type) -> Type:
        return U8()


class I8(Numerical):
    def is_signed() -> bool:
        return True

    def __eq__(self, rhs: Type):
        return isinstance(rhs, I8)

    def __str__(self):
        return "i8"

    def infer_from_number_literal(self, literal: Type) -> Type:
        return I8()


class NumberLiteral(Numerical):
    def is_signed() -> bool:
        return False

    def __eq__(self, rhs: Type):
        return isinstance(rhs, NumberLiteral)

    def __str__(self):
        return "<number literal>"

    def infer(self, to: Type) -> Type:
        return to.infer_from_number_literal(self)


class Bool(Type):
    def __eq__(self, rhs: Type):
        return isinstance(rhs, Bool)

    def __str__(self):
        return "bool"


class Callable(Type):
    def __init__(self, return_type: Type, parameter_types: [Type]):
        self.return_type = return_type
        self.parameter_types = parameter_types

    def __eq__(self, rhs: Type):
        return (
            isinstance(rhs, Callable)
            and self.return_type == rhs.return_type
            and self.parameter_types == rhs.parameter_types
        )

    def __str__(self):
        parameters = ""
        if self.parameter_types:
            for param in self.parameter_types:
                parameters += str(param) + ","
                parameters = parameters.rstrip(",")
        return f"Callable[[{str(parameters)}], {str(self.return_type)}]"
