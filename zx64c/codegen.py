from __future__ import annotations

from zx64c.ast import (
    Program,
    Block,
    If,
    Print,
    Assignment,
    Addition,
    Negation,
    Identifier,
    Unsignedint,
    Bool,
)
from zx64c.ast import AstVisitor, T

INDENTATION = "    "

_LABEL = 0


def make_label() -> str:
    return f"LB{_LABEL}"


class Environment:
    def __init__(self):
        self._variable_offsets = {}

    def add_variable(self, name: str):
        self._variable_offsets[name] = -2
        self._variable_offsets = {
            key: offset + 2 for key, offset in self._variable_offsets.items()
        }

    def get_variable_offset(self, name: str) -> int:
        return self._variable_offsets[name]


class SjasmplusSnapshotVisitor(AstVisitor[None]):
    def __init__(self, codegen: Z80CodegenVisitor, source_name: str):
        self._codegen = codegen
        self._source_name = source_name

    def visit_program(self, node: Program) -> None:
        print(f"{INDENTATION}DEVICE ZXSPECTRUM48")
        self._codegen.visit_program(node)
        print("")
        print(f'{INDENTATION}SAVESNA "{self._source_name}.sna", start')

    def visit_block(self, node: Block) -> None:
        self._codegen.visit_block(node)

    def visit_if(self, node: If) -> None:
        self._codegen.visit_if(node)

    def visit_print(self, node: Print) -> None:
        self._codegen.visit_print(node)

    def visit_assignment(self, node: Assignment) -> None:
        self._codegen.visit_assignment(node)

    def visit_addition(self, node: Addition) -> None:
        self._codegen.visit_addition(node)

    def visit_negation(self, node: Negation) -> None:
        self._codegen.visit_negation(node)

    def visit_identifier(self, node: Identifier) -> None:
        self._codegen.visit_identifier(node)

    def visit_unsignedint(self, node: Unsignedint) -> None:
        self._codegen.visit_unsignedint(node)


class Z80CodegenVisitor(AstVisitor[None]):
    def __init__(self, environment: Environment):
        self._environment = environment

    def visit_program(self, node: Program) -> None:
        print(f"{INDENTATION}org $8000")
        print("")
        print("start:")
        for statement in node.statements:
            statement.visit(self)
        print(f"{INDENTATION}ret")

    def visit_block(self, node: Block) -> None:
        for statement in node.statements:
            statement.visit(self)

    def visit_if(self, node: If) -> None:
        label = make_label()
        node.condition.visit(self)
        print(f"{INDENTATION}cp $01")
        print(f"{INDENTATION}jp nz, {label}")
        node.consequence.visit(self)
        print(f"{label}:")

    def visit_print(self, node: Print) -> T:
        node.expression.visit(self)
        print(f"{INDENTATION}rst $10")

    def visit_assignment(self, node: Assignment) -> None:
        node.rhs.visit(self)
        self._environment.add_variable(node.name)
        print(f"{INDENTATION}push af")

    def visit_addition(self, node: Addition) -> None:
        node.lhs.visit(self)
        print(f"{INDENTATION}ld b, a")
        node.rhs.visit(self)
        print(f"{INDENTATION}adc a, b")

    def visit_negation(self, node: Negation) -> None:
        node.expression.visit(self)
        print(f"{INDENTATION}neg")

    def visit_identifier(self, node: Identifier) -> None:
        offset = self._environment.get_variable_offset(node.value)
        print(f"{INDENTATION}ld hl, $00")
        print(f"{INDENTATION}add hl, sp")
        print(f"{INDENTATION}ld ix, hl")
        print(f"{INDENTATION}ld a, (ix + {offset + 1})")

    def visit_unsignedint(self, node: Unsignedint) -> None:
        print(f"{INDENTATION}ld a, {node.value}")

    def visit_bool(self, node: Bool) -> None:
        value = 1 if node.value else 0
        print(f"{INDENTATION}ld a, {value}")
