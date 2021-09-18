from __future__ import annotations

from zx64c.ast import (
    SourceContext,
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
    Unsignedint,
    Bool,
)
from zx64c.ast import AstVisitor
from zx64c.types import Type, VOID, U8, BOOL
from zx64c.typechecker.errors import (
    TypecheckError,
    AlreadyDefinedVariableError,
    CombinedTypecheckError,
    TypeMismatchError,
    NoReturnError,
    UndefinedTypeError,
    UndefinedVariableError,
)


class EnvironmentStack:
    def __init__(self):
        self._scopes: [Scope] = []
        self._defined_types = [VOID, U8, BOOL]

    @property
    def _current_scope(self) -> Scope:
        print(len(self._scopes))
        return self._scopes[-1]

    def push_scope(self, scope: Scope):
        self._scopes.append(scope)

    def pop_scope(self):
        self._scopes.pop()

    def add_type(self, udt: Type):
        self._current_scope.append(udt)

    def add_variable(self, name: str, var_type: Type, context: SourceContext):
        self._current_scope.add_variable(name, var_type, context)

    def has_variable(self, name):
        for scope in self._scopes:
            if scope.has_variable(name):
                return True
        return False

    def get_variable_type(self, name: str, context: SourceContext) -> Type:
        """
        :param context: used to create error in case the variable is not defined
        """
        for scope in reversed(self._scopes):
            print(scope._variable_types)
            try:
                return scope.get_variable_type(name, context)
            except UndefinedVariableError:
                continue
        raise UndefinedVariableError(name, context)


class Scope:
    def __init__(self):
        self._variable_types = {}
        self._defined_types = [VOID, U8, BOOL]

    def add_type(self, udt: Type):
        self._defined_types.append(udt)

    def add_variable(self, name: str, var_type: Type, context: SourceContext):
        if var_type not in self._defined_types:
            raise UndefinedTypeError(var_type, context)

        self._variable_types[name] = var_type

    def has_variable(self, name):
        return name in self._variable_types

    def get_variable_type(self, name: str, context: SourceContext) -> Type:
        """
        :param context: used to create error in case the variable is not defined
        """
        try:
            return self._variable_types[name]
        except KeyError:
            raise UndefinedVariableError(name, context)


class TypecheckerVisitor(AstVisitor[Type]):
    def __init__(self, environment: EnvironmentStack = None):
        if environment is None:
            environment = EnvironmentStack()
        self._environment = environment
        self._current_function_return_type: Type = VOID
        self._return_has_occured = False

    def visit_program(self, node: Program) -> Type:
        type_errors: [TypecheckError] = []
        for function in node.functions:
            try:
                function.visit(TypecheckerVisitor(self._environment))
            except TypecheckError as e:
                type_errors.append(e)

        if type_errors:
            raise CombinedTypecheckError(type_errors)

        return VOID

    def visit_function(self, node: Function) -> Type:
        self._current_function_return_type = node.return_type
        self._return_has_occured = False

        function_scope = Scope()
        for parameter in node.parameters:
            function_scope.add_variable(parameter.name, parameter.type_id, node.context)
        self._environment.push_scope(function_scope)

        node.code_block.visit(self)
        if not self._return_has_occured and self._current_function_return_type != VOID:
            raise NoReturnError(node.return_type, node.name, node.context)

        self._environment.pop_scope()
        return VOID

    def visit_block(self, node: Block) -> Type:
        self._environment.push_scope(Scope())

        type_errors: [TypecheckError] = []
        for statement in node.statements:
            try:
                statement.visit(self)
            except TypecheckError as e:
                type_errors.append(e)

        if type_errors:
            raise CombinedTypecheckError(type_errors)

        self._environment.pop_scope()
        return VOID

    def visit_if(self, node: If) -> Type:
        condition_type = node.condition.visit(self)
        if condition_type != BOOL:
            raise TypeMismatchError(BOOL, condition_type, node.condition.context)

        node.consequence.visit(self)
        return VOID

    def visit_print(self, node: Print) -> Type:
        node.expression.visit(self)

        return VOID

    def visit_let(self, node: Let) -> Type:
        rhs_type = node.rhs.visit(self)

        if self._environment.has_variable(node.name):
            raise AlreadyDefinedVariableError(node.name, node.context)

        self._environment.add_variable(node.name, node.var_type, node.context)

        variable_type = self._environment.get_variable_type(node.name, node.context)
        if variable_type != rhs_type:
            raise TypeMismatchError(variable_type, rhs_type, node.context)

        return VOID

    def visit_assignment(self, node: Assignment) -> Type:
        rhs_type = node.rhs.visit(self)

        variable_type = self._environment.get_variable_type(node.name, node.context)
        if variable_type != rhs_type:
            raise TypeMismatchError(variable_type, rhs_type, node.context)

        return VOID

    def visit_return(self, node: Return) -> Type:
        return_type = node.expr.visit(self)
        function_return_type = self._current_function_return_type

        if return_type != function_return_type:
            raise TypeMismatchError(function_return_type, return_type, node.context)

        self._return_has_occured = True

        return VOID

    def visit_addition(self, node: Addition) -> Type:
        lhs_type = node.lhs.visit(self)
        rhs_type = node.rhs.visit(self)

        if lhs_type != U8:
            raise TypeMismatchError(U8, lhs_type, node.lhs.context)

        if rhs_type != U8:
            raise TypeMismatchError(U8, rhs_type, node.rhs.context)

        return U8

    def visit_negation(self, node: Negation) -> Type:
        expression_type = node.expression.visit(self)

        if expression_type != U8:
            raise TypeMismatchError(U8, expression_type, node.context)

        return expression_type

    def visit_identifier(self, node: Identifier) -> Type:
        return self._environment.get_variable_type(node.value, node.context)

    def visit_unsignedint(self, node: Unsignedint) -> Type:
        return U8

    def visit_bool(self, node: Bool) -> Type:
        return BOOL
