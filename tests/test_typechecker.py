import pytest

from zx64c.ast import SourceContext, Identifier, Assignment, Print, Parameter
from tests.ast import (
    TEST_CONTEXT,
    FunctionTC,
    BlockTC,
    IfTC,
    PrintTC,
    LetTC,
    AssignmentTC,
    ReturnTC,
    AdditionTC,
    NegationTC,
    UnsignedintTC,
    IdentifierTC,
    BoolTC,
)
from zx64c.types import Type, VOID, U8, BOOL
from zx64c.typechecker import (
    TypecheckerVisitor,
    Scope,
    EnvironmentStack,
)
from zx64c.typechecker.errors import (
    AlreadyDefinedVariableError,
    CombinedTypecheckError,
    TypeMismatchError,
    NoReturnError,
    UndefinedTypeError,
    UndefinedVariableError,
)


def test_unsignedint_node_type():
    ast = UnsignedintTC(1)

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == U8


def test_bool_node_type():
    ast = BoolTC(True)

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == BOOL


def test_addition_node_type():
    ast = AdditionTC(UnsignedintTC(1), UnsignedintTC(2))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == U8


@pytest.mark.parametrize(
    "lhs_node, rhs_node, expected_type, got_type",
    [
        (BoolTC(True), UnsignedintTC(1), U8, BOOL),
        (UnsignedintTC(1), BoolTC(True), U8, BOOL),
    ],
)
def test_addition_node_type_mismatch(lhs_node, rhs_node, expected_type, got_type):
    ast = AdditionTC(lhs_node, rhs_node)

    try:
        ast.visit(TypecheckerVisitor())
    except TypeMismatchError as e:
        assert e == TypeMismatchError(expected_type, got_type, TEST_CONTEXT)
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
    except UndefinedVariableError as e:
        assert e == UndefinedVariableError("x", TEST_CONTEXT)
        return

    assert False, "Expected undefined variable exception not raised"


def test_addition_node_type_mismatch_with_variable():
    ast = BlockTC(
        [
            LetTC("x", BOOL, BoolTC(True)),
            AdditionTC(IdentifierTC("x"), UnsignedintTC(1)),
        ]
    )

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        e == CombinedTypecheckError([TypeMismatchError(U8, BOOL, TEST_CONTEXT)])
        return

    assert False, "Expected type error exception not raised"


def test_identifier_node_type():
    ast = IdentifierTC("x")
    scope = Scope()
    scope.add_variable("x", U8, TEST_CONTEXT)
    environment = EnvironmentStack()
    environment.push_scope(scope)

    typecheck_result = ast.visit(TypecheckerVisitor(environment))

    assert typecheck_result is U8


def test_identifier_node_type_with_undefined_variable():
    ast = IdentifierTC("x")
    empty_scope = Scope()

    try:
        ast.visit(TypecheckerVisitor(empty_scope))
    except UndefinedVariableError as e:
        assert e == UndefinedVariableError("x", TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"


def test_negation_node():
    ast = NegationTC(UnsignedintTC(1))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is U8


def test_negation_node_type_mismatch():
    ast = NegationTC(BoolTC(True))

    try:
        ast.visit(TypecheckerVisitor())
    except TypeMismatchError as e:
        assert e == TypeMismatchError(U8, BOOL, TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"


def test_print_node_type():
    ast = PrintTC(UnsignedintTC(1))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is VOID


def test_assignment_node_type():
    scope = Scope()
    scope.add_variable("x", U8, TEST_CONTEXT)
    ast = AssignmentTC("x", UnsignedintTC(1))

    typecheck_result = ast.visit(TypecheckerVisitor(scope))

    assert typecheck_result is VOID


def test_assignment_node_raises_mismatch():
    ast = BlockTC([LetTC("x", U8, UnsignedintTC(1)), AssignmentTC("x", BoolTC(True))])

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError([TypeMismatchError(U8, BOOL, TEST_CONTEXT)])
        return

    assert False, "Expected type error exception not raised"


def test_let_node():
    environment = EnvironmentStack()
    environment.push_scope(Scope())
    ast = LetTC("x", U8, UnsignedintTC(1))

    typecheck_result = ast.visit(TypecheckerVisitor(environment))

    assert typecheck_result is VOID
    assert environment.get_variable_type("x", TEST_CONTEXT) == U8


def test_let_node_raises_undefined_type():
    environment = EnvironmentStack()
    environment.push_scope(Scope())
    ast = LetTC("x", Type("unknown"), UnsignedintTC(1))

    try:
        ast.visit(TypecheckerVisitor(environment))
    except UndefinedTypeError as e:
        assert e == UndefinedTypeError(Type("unknown"), TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"


def test_let_node_raises_in_if_mismatch():
    ast = BlockTC(
        [
            LetTC("x", U8, UnsignedintTC(1)),
            IfTC(BoolTC(True), AssignmentTC("x", BoolTC(True))),
        ]
    )

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError([TypeMismatchError(U8, BOOL, TEST_CONTEXT)])
        return

    assert False, "Expected type error exception not raised"


def test_let_for_already_defined_variable_raises():
    ast = BlockTC(
        [
            LetTC("x", U8, UnsignedintTC(1)),
            IfTC(BoolTC(True), LetTC("x", U8, BoolTC(True))),
        ]
    )

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError(
            [AlreadyDefinedVariableError("x", TEST_CONTEXT)]
        )
        return

    assert False, "Expected type error exception not raised"


def test_program_node_type():
    ast = BlockTC([LetTC("x", U8, UnsignedintTC(1))])

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is VOID


def test_program_node_type_with_errors():
    context = SourceContext(1, 5)
    identifier = Identifier("y", context)
    ast = BlockTC([LetTC("x", U8, UnsignedintTC(1)), PrintTC(identifier)])

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError([UndefinedVariableError("y", context)])
        return

    assert False, "Expected type error exception not raised"


def test_block_node_type():
    ast = BlockTC([LetTC("x", U8, UnsignedintTC(1)), PrintTC(UnsignedintTC(1))])

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is VOID


def test_block_node_type_combines_errors():
    context = SourceContext(1, 5)
    identifier = Identifier("undefined", context)
    ast = BlockTC(
        [Assignment("x", UnsignedintTC(1), context), Print(identifier, context)]
    )

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError(
            [
                UndefinedVariableError("x", context),
                UndefinedVariableError("undefined", context),
            ]
        )
        return

    assert False, "Expected type error exception not raised"


def test_if_node_type():
    scope = Scope()
    environment = EnvironmentStack()
    environment.push_scope(scope)

    ast = IfTC(BoolTC(True), LetTC("x", U8, UnsignedintTC(1)))

    typecheck_result = ast.visit(TypecheckerVisitor(environment))

    assert typecheck_result is VOID


def test_if_node_type_mismatches_on_not_bool():
    ast = IfTC(UnsignedintTC(1), LetTC("x", U8, UnsignedintTC(1)))

    try:
        ast.visit(TypecheckerVisitor())
    except TypeMismatchError as e:
        assert e == TypeMismatchError(BOOL, U8, TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"


def test_function_node_with_void_return_type_without_return():
    ast = FunctionTC(
        "main", [], VOID, BlockTC([BoolTC(True), LetTC("x", U8, UnsignedintTC(1))])
    )

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is VOID


def test_function_node_with_return_type_with_return():
    ast = FunctionTC("main", [], U8, BlockTC([ReturnTC(UnsignedintTC(1))]))
    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is VOID


def test_function_node_with_wrong_return_raises():
    ast = FunctionTC("main", [], VOID, BlockTC([ReturnTC(UnsignedintTC(1))]))

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError([TypeMismatchError(VOID, U8, TEST_CONTEXT)])
        return

    assert False, "Expected type error exception not raised"


def test_function_node_without_return_type_with_multiple_wrong_return_raises():
    ast = FunctionTC(
        "main", [], VOID, BlockTC([ReturnTC(UnsignedintTC(1)), ReturnTC(BoolTC(True))])
    )

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError(
            [
                TypeMismatchError(VOID, U8, TEST_CONTEXT),
                TypeMismatchError(VOID, BOOL, TEST_CONTEXT),
            ]
        )
        return

    assert False, "Expected type error exception not raised"


def test_function_node_with_multiple_valid_returns():
    ast = FunctionTC(
        "main",
        [],
        U8,
        BlockTC([ReturnTC(UnsignedintTC(1)), ReturnTC(UnsignedintTC(1))]),
    )

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is VOID


def test_function_node_with_return_type_without_any_return_raises_noreturn():
    ast = FunctionTC("main", [], U8, BlockTC([]))

    try:
        ast.visit(TypecheckerVisitor())
    except NoReturnError as e:
        assert e == NoReturnError(U8, "main", TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"


def test_function_node_parameters_can_be_accessed():
    environment = EnvironmentStack()
    environment.push_scope(Scope())
    ast = FunctionTC(
        "main", [Parameter("x", U8)], VOID, BlockTC([PrintTC(IdentifierTC("x"))])
    )

    typecheck_result = ast.visit(TypecheckerVisitor(environment))

    assert typecheck_result == VOID


def test_inner_code_blocks_dont_leak_variables():
    ast = FunctionTC(
        "main",
        [],
        VOID,
        BlockTC(
            [
                IfTC(BoolTC(True), BlockTC([LetTC("x", U8, UnsignedintTC(1))])),
                PrintTC(IdentifierTC("x")),
            ]
        ),
    )

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError([UndefinedVariableError("x", TEST_CONTEXT)])
        return

    assert False, "Expected type error exception not raised"
