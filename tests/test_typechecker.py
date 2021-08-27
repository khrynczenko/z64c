from z64c.ast import (
    Program,
    Print,
    Assignment,
    Addition,
    Negation,
    Identifier,
    Unsignedint,
)
from z64c.typechecker import (
    TypecheckerVisitor,
    Environment,
    Type,
    CombinedTypecheckErrors,
    TypeMismatch,
    UndefinedVariable,
)


def test_unsignedint_node_type():
    ast = Unsignedint(1)

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.U8


def test_addition_node_type():
    ast = Addition(Unsignedint(1), Unsignedint(2))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.U8


def test_addition_node_type_mismatch_rhs():
    ast = Addition(Unsignedint(1), Program([]))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == TypeMismatch(Type.U8, Type.VOID)


def test_addition_node_type_mismatch_lhs():
    ast = Addition(Program([]), Unsignedint(1))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == TypeMismatch(Type.U8, Type.VOID)


def test_addition_node_type_error_propagation_rhs():
    ast = Addition(Unsignedint(1), Identifier("x"))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == UndefinedVariable("x")


def test_addition_node_type_error_propagation_lhs():
    ast = Addition(Identifier("x"), Unsignedint(1))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == UndefinedVariable("x")


def test_identifier_node_type():
    ast = Identifier("x")
    environment = Environment()
    environment.add_variable("x", Type.U8)

    typecheck_result = ast.visit(TypecheckerVisitor(environment))

    assert typecheck_result is Type.U8


def test_identifier_node_type_with_undefined_variable():
    ast = Identifier("x")
    empty_environment = Environment()

    typecheck_result = ast.visit(TypecheckerVisitor(empty_environment))

    assert typecheck_result == UndefinedVariable("x")


def test_negation_node():
    ast = Negation(Unsignedint(1))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.U8


def test_negation_node_type_mismatch():
    ast = Negation(Program([]))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == TypeMismatch(Type.U8, Type.VOID)


def test_print_node_type():
    ast = Print(Unsignedint(1))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.VOID


def test_assignment_node_type():
    ast = Assignment("x", Unsignedint(1))

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.VOID


def test_program_node_type():
    ast = Program([Assignment("x", Unsignedint(1))])

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result is Type.VOID


def test_program_node_type_with_errors():
    ast = Program([Assignment("x", Unsignedint(1)), Print(Identifier("y"))])

    typecheck_result = ast.visit(TypecheckerVisitor())

    assert typecheck_result == CombinedTypecheckErrors([UndefinedVariable("y")])
