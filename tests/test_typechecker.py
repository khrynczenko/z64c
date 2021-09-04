import pytest

from zx64c.ast import SourceContext, Identifier
from tests.ast import (
    TEST_CONTEXT,
    ProgramTC,
    BlockTC,
    IfTC,
    PrintTC,
    AssignmentTC,
    AdditionTC,
    NegationTC,
    UnsignedintTC,
    IdentifierTC,
    BoolTC,
)
from zx64c.typechecker import (
    TypecheckerVisitor,
    Environment,
    Type,
    CombinedTypecheckError,
    TypeMismatch,
    UndefinedVariable,
)


def test_unsignedint_node_type():
    ast = UnsignedintTC(1)

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.U8


def test_bool_node_type():
    ast = BoolTC(True)

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.BOOL


def test_addition_node_type():
    ast = AdditionTC(UnsignedintTC(1), UnsignedintTC(2))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.U8


@pytest.mark.parametrize(
    "lhs_node, rhs_node, expected_type, got_type",
    [
        (BoolTC(True), UnsignedintTC(1), Type.U8, Type.BOOL),
        (UnsignedintTC(1), BoolTC(True), Type.U8, Type.BOOL),
    ],
)
def test_addition_node_type_mismatch(lhs_node, rhs_node, expected_type, got_type):
    ast = AdditionTC(lhs_node, rhs_node)

    try:
        ast.visit(TypecheckerVisitor())
    except TypeMismatch as e:
        assert e == TypeMismatch(expected_type, got_type, TEST_CONTEXT)
        return

    assert False, "Expected type mismatch exception not raised"


@pytest.mark.parametrize(
    "lhs_node, rhs_node",
    [(IdentifierTC("x"), UnsignedintTC(1)), (UnsignedintTC(1), IdentifierTC("x"))],
)
def test_addition_node_type_error_propagates(lhs_node, rhs_node):
    ast = AdditionTC(lhs_node, rhs_node)

    try:
        ast.visit(TypecheckerVisitor())
    except UndefinedVariable as e:
        assert e == UndefinedVariable("x", TEST_CONTEXT)
        return

    assert False, "Expected undefined variable exception not raised"


def test_addition_node_type_mismatch_with_identifier():
    ast = ProgramTC(
        [
            AssignmentTC("x", BoolTC(True)),
            AdditionTC(IdentifierTC("x"), UnsignedintTC(1)),
        ]
    )

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        e == CombinedTypecheckError([TypeMismatch(Type.U8, Type.BOOL, TEST_CONTEXT)])
        return

    assert False, "Expected type error exception not raised"


def test_identifier_node_type():
    ast = IdentifierTC("x")
    environment = Environment()
    environment.add_variable("x", Type.U8)

    typecheck_result = ast.visit(TypecheckerVisitor(environment))

    assert typecheck_result is Type.U8


def test_identifier_node_type_with_undefined_variable():
    ast = IdentifierTC("x")
    empty_environment = Environment()

    try:
        ast.visit(TypecheckerVisitor(empty_environment))
    except UndefinedVariable as e:
        assert e == UndefinedVariable("x", TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"


def test_negation_node():
    ast = NegationTC(UnsignedintTC(1))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.U8


def test_negation_node_type_mismatch():
    ast = NegationTC(BoolTC(True))

    try:
        ast.visit(TypecheckerVisitor())
    except TypeMismatch as e:
        print("X")
        assert e == TypeMismatch(Type.U8, Type.BOOL, TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"


def test_print_node_type():
    ast = PrintTC(UnsignedintTC(1))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.VOID


def test_assignment_node_type():
    ast = AssignmentTC("x", UnsignedintTC(1))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.VOID


def test_program_node_type():
    ast = ProgramTC([AssignmentTC("x", UnsignedintTC(1))])

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.VOID


def test_program_node_type_with_errors():
    context = SourceContext(1, 5)
    identifier = Identifier("y", context)
    ast = ProgramTC([AssignmentTC("x", UnsignedintTC(1)), PrintTC(identifier)])

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError([UndefinedVariable("y", context)])
        return

    assert False, "Expected type error exception not raised"


def test_block_node_type():
    ast = BlockTC([AssignmentTC("x", UnsignedintTC(1)), PrintTC(UnsignedintTC(1))])

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.VOID


def test_block_node_type_combines_errors():
    context = SourceContext(1, 5)
    identifier = Identifier("undefined", context)
    ast = BlockTC([AssignmentTC("x", UnsignedintTC(1)), PrintTC(identifier)])

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError([UndefinedVariable("undefined", context)])
        return

    assert False, "Expected type error exception not raised"


def test_if_node_type():
    ast = IfTC(BoolTC(True), AssignmentTC("x", UnsignedintTC(1)))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.VOID


def test_if_node_type_mismatches_on_not_bool():
    ast = IfTC(UnsignedintTC(1), AssignmentTC("x", UnsignedintTC(1)))

    try:
        ast.visit(TypecheckerVisitor())
    except TypeMismatch as e:
        assert e == TypeMismatch(Type.BOOL, Type.U8, TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"
