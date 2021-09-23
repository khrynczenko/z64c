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


class U8(Type):
    def __eq__(self, rhs: Type):
        return isinstance(rhs, U8)

    def __str__(self):
        return "u8"


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
