from __future__ import annotations

from z64c.ast import (
    Program,
    Print,
    Assignment,
    Addition,
    Negation,
    Identifier,
    Unsignedint,
)
from z64c.ast import AstVisitor, T

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


class SjasmplusSnapshotVisitor(AstVisitor[None]):
    def __init__(self, codegen: Z80CodegenVisitor, source_name: str):
        self._codegen = codegen
        self._source_name = source_name

    def visitProgram(self, node: Program) -> None:
        print(f"{INDENTATION}DEVICE ZXSPECTRUM48")
        self._codegen.visitProgram(node)
        print("")
        print(f'{INDENTATION}SAVESNA "{self._source_name}.sna", start')

    def visitPrint(self, node: Print) -> None:
        self._codegen.visitPrint(node)

    def visitAssigment(self, node: Assignment) -> None:
        pass
        self._codegen.visitAssigment(node)

    def visitAddition(self, node: Addition) -> None:
        pass
        self._codegen.visitAddition(node)

    def visitNegation(self, node: Negation) -> None:
        pass
        self._codegen.visitNegation(node)

    def visitIdentifier(self, node: Identifier) -> None:
        pass
        self._codegen.visitIdentifier(node)

    def visitUnsignedint(self, node: Unsignedint) -> None:
        self._codegen.visitUnsignedint(node)


class Z80CodegenVisitor(AstVisitor[None]):
    def __init__(self, environment: Environment):
        self._environment = environment

    def visitProgram(self, node: Program) -> None:
        print(f"{INDENTATION}org $8000")
        print("")
        print("start:")
        for statement in node._statements:
            statement.visit(self)
        print(f"{INDENTATION}ret")

    def visitPrint(self, node: Print) -> T:
        node._expression.visit(self)
        print(f"{INDENTATION}rst $10")

    def visitAssigment(self, node: Assignment) -> None:
        node._rhs.visit(self)
        self._environment.add_variable(node._name)
        print(f"{INDENTATION}push af")

    def visitAddition(self, node: Addition) -> None:
        node._lhs.visit(self)
        print(f"{INDENTATION}ld b, a")
        node._rhs.visit(self)
        print(f"{INDENTATION}adc a, b")

    def visitNegation(self, node: Negation) -> None:
        node._expression.visit(self)
        print(f"{INDENTATION}neg")

    def visitIdentifier(self, node: Identifier) -> None:
        offset = self._environment.get_variable_offset(node._value)
        print(f"{INDENTATION}ld hl, $00")
        print(f"{INDENTATION}add hl, sp")
        print(f"{INDENTATION}ld ix, hl")
        print(f"{INDENTATION}ld a, (ix + {offset + 1})")

    def visitUnsignedint(self, node: Unsignedint) -> None:
        print(f"{INDENTATION}ld a, {node._value}")
