from __future__ import annotations

from zx64c.ast import (
    Program,
    Function,
    Block,
    If,
    Print,
    Let,
    Return,
    Assignment,
    Addition,
    Negation,
    Identifier,
    FunctionCall,
    Unsignedint,
    Bool,
)
from zx64c.ast import AstVisitor

INDENTATION = "    "

_LABEL = 0


def make_label() -> str:
    return f"LB{_LABEL}"


class Environment:
    def __init__(self):
        self._variable_offsets = {}
        # ^^^ these offsets are with respect to the stack pointer

        self._parameters_offsets = {}
        # ^^^ these offsets are with respect to the frame pointer

    def add_parameter(self, name: str):
        self._parameters_offsets[name] = 2
        self._parameters_offsets = {
            key: offset + 2 for key, offset in self._parameters_offsets.items()
        }

    def add_variable(self, name: str):
        self._variable_offsets[name] = -2
        self._variable_offsets = {
            key: offset + 2 for key, offset in self._variable_offsets.items()
        }

    def is_parameter(self, name: str) -> bool:
        if name in self._variable_offsets:
            return False
        return name in self._parameters_offsets

    def get_variable_offset(self, name: str) -> int:
        if name in self._variable_offsets:
            return self._variable_offsets[name]
        else:
            return self._parameters_offsets[name]


class SjasmplusSnapshotVisitor(AstVisitor[None]):
    def __init__(self, codegen: Z80CodegenVisitor, source_name: str):
        self._codegen = codegen
        self._source_name = source_name

    def visit_program(self, node: Program) -> None:
        print(f"{INDENTATION}DEVICE ZXSPECTRUM48")
        self._codegen.visit_program(node)
        print("")
        print(f'{INDENTATION}SAVESNA "{self._source_name}.sna", main')

    def visit_function(self, node: Function) -> None:
        self._codegen.visit_return(node)

    def visit_block(self, node: Block) -> None:
        self._codegen.visit_block(node)

    def visit_if(self, node: If) -> None:
        self._codegen.visit_if(node)

    def visit_print(self, node: Print) -> None:
        self._codegen.visit_print(node)

    def visit_let(self, node: Let) -> None:
        self._codegen.visit_let(node)

    def visit_return(self, node: Return) -> None:
        self._codegen.visit_return(node)

    def visit_assignment(self, node: Assignment) -> None:
        self._codegen.visit_assignment(node)

    def visit_addition(self, node: Addition) -> None:
        self._codegen.visit_addition(node)

    def visit_negation(self, node: Negation) -> None:
        self._codegen.visit_negation(node)

    def visit_function_call(self, node: FunctionCall) -> None:
        self._codegen.visit_function_call(node)

    def visit_identifier(self, node: Identifier) -> None:
        self._codegen.visit_identifier(node)

    def visit_unsignedint(self, node: Unsignedint) -> None:
        self._codegen.visit_unsignedint(node)

    def visit_bool(self, node: Bool) -> None:
        self._codegen.visit_unsignedint(node)


class Z80CodegenVisitor(AstVisitor[None]):
    def __init__(self, environment: Environment):
        self._environment = environment

    @staticmethod
    def _init_function() -> None:
        """
        Saves frme pointer of the caller onto the stack. Then stores stack
        pointer to the memory so it will act as a new frame pointer.
        After this stack should look as follow:
        ------- $02
        |     |
        ------- $01
        |     |
        ------- ...
        |     |
        ------- <- sp and frame_pointer point here after finishing this method
        | $?? | = frame_pointer of the caller
        -------
        | $?? | = address where to return (push pc result of the caller)
        -------
        | $?? | = argument for the first parameter
        -------
        | $?? | = argument for the second parameter ...
        -------

        """
        print(f"{INDENTATION}; BEGIN FUNCTION INITIALIZATION")
        print(f"{INDENTATION}ld hl, (frame_pointer)")
        print(f"{INDENTATION}push hl")
        print(f"{INDENTATION}ld (frame_pointer), sp")
        print(f"{INDENTATION}; END FUNCTION INITIALIZATION")

    @staticmethod
    def _deinit_function() -> None:
        """
        We dealloacte the stack first by loading the frame_pointer to it. We
        then load whats on top of the stack (it should be the callers frame
        pointer) to the frame_pointer.
        """
        print(f"{INDENTATION}; BEGIN FUNCTION DEINITIALIZATION")
        print(f"{INDENTATION}ld sp, (frame_pointer)")
        print(f"{INDENTATION}ld hl, $00")
        print(f"{INDENTATION}add hl, sp")
        print(f"{INDENTATION}ld bc, (hl)")
        print(f"{INDENTATION}ld (frame_pointer), bc")
        # ^ restore frame pointer for the caller
        print(f"{INDENTATION}pop bc")
        # ^ pop stack one item so now it points to the caller address
        print(f"{INDENTATION}ret")
        print(f"{INDENTATION}; END FUNCTION DEINITIALIZATION")

    def visit_program(self, node: Program) -> None:
        print(f"{INDENTATION}org $8000")
        print("")
        print(f"{INDENTATION}jp main")
        print("")
        print("frame_pointer:")
        print(f"{INDENTATION}dw 0")
        print("")
        for function in node.functions:
            environment = Environment()
            for parameter in reversed(function.parameters):
                # ^ we add them in reverse so it is easier to reach them on the
                #   stack
                environment.add_parameter(parameter.name)
            visitor = Z80CodegenVisitor(environment)
            function.visit(visitor)

    def visit_function(self, node: Function) -> None:
        print(f"{node.name}:")
        self._init_function()
        node.code_block.visit(self)
        self._deinit_function()

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

    def visit_print(self, node: Print) -> None:
        node.expression.visit(self)
        print(f"{INDENTATION}rst $10")

    def visit_let(self, node: Let) -> None:
        node.rhs.visit(self)
        self._environment.add_variable(node.name)
        print(f"{INDENTATION}push af")

    def visit_return(self, node: Return) -> None:
        node.expr.visit(self)
        self._deinit_function()

    def visit_assignment(self, node: Assignment) -> None:
        node.rhs.visit(self)
        offset = self._environment.get_variable_offset(node.value)
        print(f"{INDENTATION}ld hl, $00")
        print(f"{INDENTATION}add hl, sp")
        print(f"{INDENTATION}ld ix, hl")
        print(f"{INDENTATION}ld (ix + {offset + 1}), a")

    def visit_addition(self, node: Addition) -> None:
        node.lhs.visit(self)
        print(f"{INDENTATION}ld b, a")
        node.rhs.visit(self)
        print(f"{INDENTATION}adc a, b")

    def visit_negation(self, node: Negation) -> None:
        node.expression.visit(self)
        print(f"{INDENTATION}neg")

    def visit_function_call(self, node: FunctionCall) -> None:
        for arg_expression in node.arguments:
            arg_expression.visit(self)
            print(f"{INDENTATION}push af")
        print(f"{INDENTATION}call {node.function_name}")
        for arg_expression in node.arguments:
            # we need to deallocate that we pushed on the stack as arguments
            # to the callee as it is no longer needed
            print(f"{INDENTATION}pop bc")

    def visit_identifier(self, node: Identifier) -> None:
        offset = self._environment.get_variable_offset(node.value)
        if self._environment.is_parameter(node.value):
            # we offset from frame pointer
            print(f"{INDENTATION}ld hl, (frame_pointer)")
        else:
            # we offset from stack pointer
            print(f"{INDENTATION}ld hl, $00")
            print(f"{INDENTATION}add hl, sp")
        print(f"{INDENTATION}ld ix, hl")
        print(f"{INDENTATION}ld a, (ix + {offset + 1})")

    def visit_unsignedint(self, node: Unsignedint) -> None:
        print(f"{INDENTATION}ld a, {node.value}")

    def visit_bool(self, node: Bool) -> None:
        value = 1 if node.value else 0
        print(f"{INDENTATION}ld a, {value}")
