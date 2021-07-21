from __future__ import annotations

from typing import List


class Ast:
    pass


class Program(Ast):
    def __init__(self, statements: List[Ast]):
        self._statements = statements

    def __eq__(self, rhs: Program) -> bool:
        return self._statements == rhs._statements


class Print(Ast):
    def __init__(self, expression: Ast):
        self._expression = expression

    def __eq__(self, rhs: Print) -> bool:
        return self._expression == rhs._expression


class Assignment(Ast):
    def __init__(self, name: str, rhs: Ast):
        self._name = name
        self._rhs = rhs

    def __eq__(self, rhs: Assignment) -> bool:
        return self._name == rhs._name and self._rhs == rhs._rhs


class Addition(Ast):
    def __init__(self, lhs: Ast, rhs: Ast):
        self._lhs = lhs
        self._rhs = rhs

    def __eq__(self, rhs: Addition) -> bool:
        return self._lhs == rhs._lhs and self._rhs == rhs._rhs


class Multiplication(Ast):
    def __init__(self, lhs: Ast, rhs: Ast):
        self._lhs = lhs
        self._rhs = rhs

    def __eq__(self, rhs: Multiplication) -> bool:
        return self._lhs == rhs._lhs and self._rhs == rhs._rhs


class Negation(Ast):
    def __init__(self, expression: Ast):
        self._expression = expression

    def __eq__(self, rhs: Negation) -> bool:
        return self._expression == rhs._expression


class Identifier(Ast):
    def __init__(self, value: str):
        self._value = value

    def __eq__(self, rhs: Identifier) -> bool:
        return self._value == rhs._value


class Unsignedint(Ast):
    def __init__(self, value: int):
        self._value = value

    def __eq__(self, rhs: Unsignedint) -> bool:
        return self._value == rhs._value
