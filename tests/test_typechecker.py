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
    EqualTC,
    NotEqualTC,
    AdditionTC,
    NegationTC,
    FunctionCallTC,
    UnsignedintTC,
    IdentifierTC,
    BoolTC,
)
from zx64c.types import (
    I8,
    U8,
    Bool,
    Void,
    TypeIdentifier,
    Callable,
)
from zx64c.typechecker import (
    TypecheckerVisitor,
    Scope,
    EnvironmentStack,
)
from zx64c.typechecker.errors import (
    AlreadyDefinedVariableError,
    CombinedTypecheckError,
    TypeMismatchError,
    ExpectedNumericalTypeError,
    NoReturnError,
    UndefinedTypeError,
    UndefinedVariableError,
    NotFunctionCall,
    NotEnoughArguments,
    TooManyArguments,
)


def test_unsignedint_node_type():
    ast = UnsignedintTC(1)

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == U8()


def test_bool_node_type():
    ast = BoolTC(True)

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == Bool()


@pytest.mark.parametrize(
    "equality_ast, lhs_node, rhs_node, expected_type, got_type",
    [
        (EqualTC, UnsignedintTC(1), BoolTC(True), U8(), Bool()),
        (EqualTC, BoolTC(True), UnsignedintTC(1), Bool(), U8()),
        (NotEqualTC, UnsignedintTC(1), BoolTC(True), U8(), Bool()),
        (NotEqualTC, BoolTC(True), UnsignedintTC(1), Bool(), U8()),
    ],
)
def test_equality_operators_raise_on_mismatch(
    equality_ast, lhs_node, rhs_node, expected_type, got_type
):
    ast = equality_ast(lhs_node, rhs_node)

    try:
        ast.visit(TypecheckerVisitor())
    except TypeMismatchError as e:
        assert e == TypeMismatchError(expected_type, got_type, TEST_CONTEXT)
        return

    assert False, "Expected type mismatch exception not raised"


def test_addition_node_type():
    ast = AdditionTC(UnsignedintTC(1), UnsignedintTC(2))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == U8()


def test_addition_raises_on_not_numerical_types():
    ast = AdditionTC(BoolTC(True), UnsignedintTC(2))

    try:
        ast.visit(TypecheckerVisitor())
    except ExpectedNumericalTypeError as e:
        assert e == ExpectedNumericalTypeError(Bool(), TEST_CONTEXT)
        return

    assert False, "Expected type mismatch exception not raised"


@pytest.mark.parametrize(
    "lhs_node, rhs_node, expected_type, got_type",
    [
        (UnsignedintTC(1), NegationTC(UnsignedintTC(1)), U8(), I8()),
        (NegationTC(UnsignedintTC(1)), UnsignedintTC(1), I8(), U8()),
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
            LetTC("x", Bool(), BoolTC(True)),
            AdditionTC(IdentifierTC("x"), UnsignedintTC(1)),
        ]
    )

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        e == CombinedTypecheckError([TypeMismatchError(U8(), Bool(), TEST_CONTEXT)])
        return

    assert False, "Expected type error exception not raised"


def test_negation_node_returns_signed_type():
    ast = NegationTC(UnsignedintTC(2))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == I8()


def test_identifier_node_type():
    ast = IdentifierTC("x")
    scope = Scope()
    scope.add_variable("x", U8(), TEST_CONTEXT)
    environment = EnvironmentStack()
    environment.push_scope(scope)

    typecheck_result = ast.visit(TypecheckerVisitor(environment))

    assert typecheck_result == U8()


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

    assert typecheck_result == I8()


def test_negation_node_raises_on_non_numerical_type():
    ast = NegationTC(BoolTC(True))

    try:
        ast.visit(TypecheckerVisitor())
    except ExpectedNumericalTypeError as e:
        assert e == ExpectedNumericalTypeError(Bool(), TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"


def test_print_node_type():
    ast = PrintTC(UnsignedintTC(1))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == Void()


def test_assignment_node_type():
    scope = Scope()
    scope.add_variable("x", U8(), TEST_CONTEXT)
    ast = AssignmentTC("x", UnsignedintTC(1))

    typecheck_result = ast.visit(TypecheckerVisitor(scope))

    assert typecheck_result == Void()


def test_assignment_node_raises_mismatch():
    ast = BlockTC([LetTC("x", U8(), UnsignedintTC(1)), AssignmentTC("x", BoolTC(True))])

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError(
            [TypeMismatchError(U8(), Bool(), TEST_CONTEXT)]
        )
        return

    assert False, "Expected type error exception not raised"


def test_assignment_node_with_function_call_raises_mismatch():
    environment = EnvironmentStack()
    scope = Scope()
    scope.add_variable("f", Callable(I8(), []), TEST_CONTEXT)
    environment.push_scope(scope)

    ast = BlockTC(
        [LetTC("x", U8(), UnsignedintTC(1)), AssignmentTC("x", FunctionCallTC("f", []))]
    )

    try:
        ast.visit(TypecheckerVisitor(environment))
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError(
            [TypeMismatchError(U8(), I8(), TEST_CONTEXT)]
        )
        return

    assert False, "Expected type error exception not raised"


def test_let_node():
    environment = EnvironmentStack()
    environment.push_scope(Scope())
    ast = LetTC("x", U8(), UnsignedintTC(1))

    typecheck_result = ast.visit(TypecheckerVisitor(environment))

    assert typecheck_result == Void()
    assert environment.get_variable_type("x", TEST_CONTEXT) == U8()


def test_let_node_raises_undefined_type():
    environment = EnvironmentStack()
    environment.push_scope(Scope())
    ast = LetTC("x", TypeIdentifier("unknown"), UnsignedintTC(1))

    try:
        ast.visit(TypecheckerVisitor(environment))
    except UndefinedTypeError as e:
        assert e == UndefinedTypeError(TypeIdentifier("unknown"), TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"


def test_let_node_resolves_type_identifier():
    environment = EnvironmentStack()
    environment.push_scope(Scope())
    environment.add_type("MyU8", U8())
    ast = LetTC("x", TypeIdentifier("MyU8"), UnsignedintTC(1))

    ast.visit(TypecheckerVisitor(environment)) == Void()


def test_let_node_raises_in_if_mismatch():
    ast = BlockTC(
        [
            LetTC("x", U8(), UnsignedintTC(1)),
            IfTC(BoolTC(True), AssignmentTC("x", BoolTC(True))),
        ]
    )

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError(
            [TypeMismatchError(U8(), Bool(), TEST_CONTEXT)]
        )
        return

    assert False, "Expected type error exception not raised"


def test_let_for_already_defined_variable_raises():
    ast = BlockTC(
        [
            LetTC("x", U8(), UnsignedintTC(1)),
            IfTC(BoolTC(True), LetTC("x", U8(), BoolTC(True))),
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
    ast = BlockTC([LetTC("x", U8(), UnsignedintTC(1))])

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == Void()


def test_program_node_type_with_errors():
    context = SourceContext(1, 5)
    identifier = Identifier("y", context)
    ast = BlockTC([LetTC("x", U8(), UnsignedintTC(1)), PrintTC(identifier)])

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError([UndefinedVariableError("y", context)])
        return

    assert False, "Expected type error exception not raised"


def test_block_node_type():
    ast = BlockTC([LetTC("x", U8(), UnsignedintTC(1)), PrintTC(UnsignedintTC(1))])

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == Void()


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

    ast = IfTC(BoolTC(True), LetTC("x", U8(), UnsignedintTC(1)))

    typecheck_result = ast.visit(TypecheckerVisitor(environment))

    assert typecheck_result == Void()


def test_if_node_type_mismatches_on_not_bool():
    ast = IfTC(UnsignedintTC(1), LetTC("x", U8(), UnsignedintTC(1)))

    try:
        ast.visit(TypecheckerVisitor())
    except TypeMismatchError as e:
        assert e == TypeMismatchError(Bool(), U8(), TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"


def test_function_node_with_void_return_type_without_return():
    ast = FunctionTC(
        "main", [], Void(), BlockTC([BoolTC(True), LetTC("x", U8(), UnsignedintTC(1))])
    )

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == Void()


def test_function_node_with_return_type_with_return():
    ast = FunctionTC("main", [], U8(), BlockTC([ReturnTC(UnsignedintTC(1))]))
    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == Void()


def test_function_node_with_wrong_return_raises():
    ast = FunctionTC("main", [], Void(), BlockTC([ReturnTC(UnsignedintTC(1))]))

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError(
            [TypeMismatchError(Void(), U8(), TEST_CONTEXT)]
        )
        return

    assert False, "Expected type error exception not raised"


def test_function_node_without_return_type_with_multiple_wrong_return_raises():
    ast = FunctionTC(
        "main",
        [],
        Void(),
        BlockTC([ReturnTC(UnsignedintTC(1)), ReturnTC(BoolTC(True))]),
    )

    try:
        ast.visit(TypecheckerVisitor())
    except CombinedTypecheckError as e:
        assert e == CombinedTypecheckError(
            [
                TypeMismatchError(Void(), U8(), TEST_CONTEXT),
                TypeMismatchError(Void(), Bool(), TEST_CONTEXT),
            ]
        )
        return

    assert False, "Expected type error exception not raised"


def test_function_node_with_multiple_valid_returns():
    ast = FunctionTC(
        "main",
        [],
        U8(),
        BlockTC([ReturnTC(UnsignedintTC(1)), ReturnTC(UnsignedintTC(1))]),
    )

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == Void()


def test_function_node_with_return_type_without_any_return_raises_noreturn():
    ast = FunctionTC("main", [], U8(), BlockTC([]))

    try:
        ast.visit(TypecheckerVisitor())
    except NoReturnError as e:
        assert e == NoReturnError(U8(), "main", TEST_CONTEXT)
        return

    assert False, "Expected type error exception not raised"


def test_function_node_parameters_can_be_accessed():
    environment = EnvironmentStack()
    environment.push_scope(Scope())
    ast = FunctionTC(
        "main", [Parameter("x", U8())], Void(), BlockTC([PrintTC(IdentifierTC("x"))])
    )

    typecheck_result = ast.visit(TypecheckerVisitor(environment))

    assert typecheck_result == Void()


def test_inner_code_blocks_dont_leak_variables():
    ast = FunctionTC(
        "main",
        [],
        Void(),
        BlockTC(
            [
                IfTC(BoolTC(True), BlockTC([LetTC("x", U8(), UnsignedintTC(1))])),
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


def test_function_call_node():
    environment = EnvironmentStack()
    environment.push_scope(Scope())
    environment.add_variable("f", Callable(Void(), [U8(), Bool()]), TEST_CONTEXT)
    ast = FunctionCallTC("f", [UnsignedintTC(1), BoolTC(True)])

    typecheck_result = ast.visit(TypecheckerVisitor(environment))

    assert typecheck_result == Void()


def test_function_call_node_raises_when_not_a_function():
    environment = EnvironmentStack()
    environment.push_scope(Scope())
    environment.add_variable("f", U8(), TEST_CONTEXT)
    ast = FunctionCallTC("f", [UnsignedintTC(1), BoolTC(True)])

    try:
        ast.visit(TypecheckerVisitor(environment))
    except NotFunctionCall as e:
        assert e == NotFunctionCall("f", TEST_CONTEXT)
        return


def test_function_call_node_raises_when_too_many_arguments():
    environment = EnvironmentStack()
    environment.push_scope(Scope())
    environment.add_variable("f", Callable(Void(), [U8()]), TEST_CONTEXT)
    ast = FunctionCallTC("f", [UnsignedintTC(1), BoolTC(True)])

    try:
        ast.visit(TypecheckerVisitor(environment))
    except TooManyArguments as e:
        assert e == TooManyArguments("f", 2, 1, TEST_CONTEXT)
        return


def test_function_call_node_raises_when_not_enough_arguments():
    environment = EnvironmentStack()
    environment.push_scope(Scope())
    environment.add_variable("f", Callable(Void(), [U8(), Bool()]), TEST_CONTEXT)
    ast = FunctionCallTC("f", [UnsignedintTC(1)])

    try:
        ast.visit(TypecheckerVisitor(environment))
    except NotEnoughArguments as e:
        assert e == NotEnoughArguments("f", 1, 2, TEST_CONTEXT)
        return
