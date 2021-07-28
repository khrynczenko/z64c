from __future__ import annotations

import abc

from typing import List, Tuple
from abc import ABC

INDENTATION = "    "


class Environment:
    def __init__(self):
        self._variables = {}
        self._idx = 0

    def add_variable(self, name: str, value):
        self._idx = self._idx + 1
        self._variables[name] = self._idx

    def get_variable(self, name: str) -> int:
        return self._variables[name]


class Ast(ABC):
    @abc.abstractmethod
    def emit(self, environment: Environment):
        pass


class Program(Ast):
    def __init__(self, statements: List[Ast]):
        self._statements = statements

    def __eq__(self, rhs: Program) -> bool:
        return self._statements == rhs._statements

    def emit(self, environment: Environment):
        print(f"{INDENTATION}org &1000")
        for statement in self._statements:
            print("")
            statement.emit(environment)
        print(f"{INDENTATION}ret")


class Print(Ast):
    def __init__(self, expression: Ast):
        self._expression = expression

    def __eq__(self, rhs: Print) -> bool:
        return self._expression == rhs._expression

    def emit(self, environment: Environment):
        self._expression.emit(environment)
        print(f"{INDENTATION}call &BB5A")


class Assignment(Ast):
    def __init__(self, name: str, rhs: Ast):
        self._name = name
        self._rhs = rhs

    def __eq__(self, rhs: Assignment) -> bool:
        return self._name == rhs._name and self._rhs == rhs._rhs

    def emit(self, environment: Environment):
        environment.add_variable(self._name)
        print(f"{INDENTATION}push a")


class Addition(Ast):
    def __init__(self, lhs: Ast, rhs: Ast):
        self._lhs = lhs
        self._rhs = rhs

    def __eq__(self, rhs: Addition) -> bool:
        return self._lhs == rhs._lhs and self._rhs == rhs._rhs

    def emit(self, environment: Environment):
        self._lhs.emit(environment)
        print(f"{INDENTATION}ld b, a")
        self._rhs.emit(environment)
        print(f"{INDENTATION}adc a, b")


class Negation(Ast):
    def __init__(self, expression: Ast):
        self._expression = expression

    def __eq__(self, rhs: Negation) -> bool:
        return self._expression == rhs._expression

    def emit(self, environment: Environment):
        self._expression.emit(environment)
        print(f"{INDENTATION}neg")


class Identifier(Ast):
    def __init__(self, value: str):
        self._value = value

    def __eq__(self, rhs: Identifier) -> bool:
        return self._value == rhs._value

    def emit(self, environment: Environment):
        idx


class Unsignedint(Ast):
    def __init__(self, value: int):
        self._value = value

    def __eq__(self, rhs: Unsignedint) -> bool:
        return self._value == rhs._value

    def emit(self, environment: Environment):
        print(f"{INDENTATION}ld a, {self._value}")
