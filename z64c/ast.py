from __future__ import annotations

import abc

from typing import List, Text
from abc import ABC

INDENTATION = "    "


class Environment:
    def __init__(self):
        self._variable_offsets = {}

    def add_variable(self, name: str):
        self._variable_offsets[name] = -1
        self._variable_offsets = {
            key: offset + 1 for key, offset in self._variable_offsets.items()
        }

    def get_variable_offset(self, name: str) -> int:
        return self._variable_offsets[name]


class Ast(ABC):
    @abc.abstractmethod
    def emit(self, environment: Environment):
        pass


class SjasmplusSnapshotProgram(Ast):
    def __init__(self, program: Program, source_name: Text):
        self._program = program
        self._source_name = source_name

    def __eq__(self, rhs: SjasmplusSnapshotProgram) -> bool:
        return self._program == rhs._program and self._source_name == rhs._source_name

    def emit(self, environment: Environment):
        print(f"{INDENTATION}DEVICE ZXSPECTRUM48")
        self._program.emit(environment)
        print("")
        print(f'{INDENTATION}SAVESNA "{self._source_name}.sna", start')


class Program(Ast):
    def __init__(self, statements: List[Ast]):
        self._statements = statements

    def __eq__(self, rhs: Program) -> bool:
        return self._statements == rhs._statements

    def emit(self, environment: Environment):
        print(f"{INDENTATION}org $8000")
        print("")
        print("start:")
        for statement in self._statements:
            statement.emit(environment)
        print(f"{INDENTATION}ret")


class Print(Ast):
    def __init__(self, expression: Ast):
        self._expression = expression

    def __eq__(self, rhs: Print) -> bool:
        return self._expression == rhs._expression

    def emit(self, environment: Environment):
        self._expression.emit(environment)
        print(f"{INDENTATION}rst $10")


class Assignment(Ast):
    def __init__(self, name: str, rhs: Ast):
        self._name = name
        self._rhs = rhs

    def __eq__(self, rhs: Assignment) -> bool:
        return self._name == rhs._name and self._rhs == rhs._rhs

    def emit(self, environment: Environment):
        self._rhs.emit(environment)
        environment.add_variable(self._name)
        print(f"{INDENTATION}push af")


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
        offset = environment.get_variable_offset(self._value)
        print(f"{INDENTATION}ld hl, $00")
        print(f"{INDENTATION}add hl, sp")
        print(f"{INDENTATION}ld ix, hl")
        print(f"{INDENTATION}ld a, (ix + {offset + 1})")


class Unsignedint(Ast):
    def __init__(self, value: int):
        self._value = value

    def __eq__(self, rhs: Unsignedint) -> bool:
        return self._value == rhs._value

    def emit(self, environment: Environment):
        print(f"{INDENTATION}ld a, {self._value}")
