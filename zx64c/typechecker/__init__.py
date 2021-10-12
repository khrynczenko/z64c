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
    Equal,
    NotEqual,
    Addition,
    Negation,
    FunctionCall,
    Identifier,
    Unsignedint,
    Bool,
)
from zx64c.ast import AstVisitor
from zx64c.types import Type, Callable, Void, I8, U8, TypeIdentifier
from zx64c.types import Bool as BoolT
from zx64c.typechecker.errors import (
    TypecheckError,
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

VOID = Void()
I8 = I8()
U8 = U8()
BOOL = BoolT()


class EnvironmentStack:
    def __init__(self):
        self._scopes: [Scope] = []
        self._defined_types = []

    @property
    def _current_scope(self) -> Scope:
        return self._scopes[-1]

    def push_scope(self, scope: Scope):
        self._scopes.append(scope)

    def pop_scope(self):
        self._scopes.pop()

    def add_type(self, name: str, type_: Type):
        self._current_scope.add_type(name, type_)

    def add_variable(self, name: str, var_type: Type, context: SourceContext):
        if isinstance(var_type, TypeIdentifier) and not self.has_type(var_type.name):
            raise UndefinedTypeError(var_type, context)

        if isinstance(var_type, TypeIdentifier):
            self._current_scope.add_variable(name, self.resolve_type(var_type), context)
        else:
            self._current_scope.add_variable(name, var_type, context)

    def has_type(self, name):
        for scope in reversed(self._scopes):
            if scope.has_type(name):
                return True
        return False

    def resolve_type(self, type_identifier: TypeIdentifier) -> Type:
        for scope in reversed(self._scopes):
            try:
                return scope.resolve_type(type_identifier.name)
            except KeyError:
                continue
        raise RuntimeError(f"Cannot resolve type indentifier {type_identifier.name}")

    def has_variable(self, name):
        for scope in reversed(self._scopes):
            if scope.has_variable(name):
                return True
        return False

    def get_variable_type(self, name: str, context: SourceContext) -> Type:
        """
        :param context: used to create error in case the variable is not defined
        """
        for scope in reversed(self._scopes):
            try:
                return scope.get_variable_type(name, context)
            except UndefinedVariableError:
                continue
        raise UndefinedVariableError(name, context)


class Scope:
    def __init__(self):
        self._variable_types = {}
        self._defined_types = {}

    def add_type(self, name: str, type_: Type):
        self._defined_types[name] = type_

    def add_variable(self, name: str, var_type: Type, context: SourceContext):
        self._variable_types[name] = var_type

    def has_type(self, name):
        return name in self._defined_types

    def has_variable(self, name):
        return name in self._variable_types

    def resolve_type(self, type_name: str) -> Type:
        return self._defined_types[type_name]

    def get_variable_type(self, name: str, context: SourceContext) -> Type:
        try:
            return self._variable_types[name]
        except KeyError:
            raise UndefinedVariableError(name, context)


class TypecheckerVisitor(AstVisitor[Type]):
    def __init__(self, environment: EnvironmentStack = None):
        if environment is None:
            environment = EnvironmentStack()
            environment.push_scope(Scope())
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

        self._environment.add_variable(node.name, node.type, node.context)

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
        if variable_type.is_numerical() and rhs_type.is_numerical():
            return VOID

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

    def visit_equal(self, node: Equal) -> Type:
        lhs_type = node.lhs.visit(self)
        rhs_type = node.rhs.visit(self)

        if lhs_type != rhs_type:
            raise TypeMismatchError(lhs_type, rhs_type, node.lhs.context)

        return BOOL

    def visit_not_equal(self, node: NotEqual) -> Type:
        return self.visit_equal(node)

    def visit_addition(self, node: Addition) -> Type:
        lhs_type = node.lhs.visit(self)
        rhs_type = node.rhs.visit(self)

        if not lhs_type.is_numerical():
            raise ExpectedNumericalTypeError(lhs_type, node.lhs.context)

        if not rhs_type.is_numerical():
            raise ExpectedNumericalTypeError(rhs_type, node.rhs.context)

        if lhs_type != rhs_type:
            raise TypeMismatchError(lhs_type, rhs_type, node.lhs.context)

        return lhs_type

    def visit_negation(self, node: Negation) -> Type:
        expression_type = node.expression.visit(self)

        if not expression_type.is_numerical():
            raise ExpectedNumericalTypeError(expression_type, node.context)

        if expression_type == U8:
            return I8

        return expression_type

    def visit_function_call(self, node: FunctionCall) -> Type:
        function_type = self._environment.get_variable_type(
            node.function_name, node.context
        )

        if not isinstance(function_type, Callable):
            raise NotFunctionCall(node.function_name, node.context)

        function_type: Callable = function_type

        arguments_count = len(node.arguments)
        parameters_count = len(function_type.parameter_types)
        if arguments_count > parameters_count:
            raise TooManyArguments(
                node.function_name, arguments_count, parameters_count, node.context
            )
        if arguments_count < parameters_count:
            raise NotEnoughArguments(
                node.function_name, arguments_count, parameters_count, node.context
            )

        for argument, parameter in zip(node.arguments, function_type.parameter_types):
            arg_type = argument.visit(self)
            if arg_type != parameter:
                raise TypeMismatchError(parameter, arg_type, node.context)

        return function_type.return_type

    def visit_identifier(self, node: Identifier) -> Type:
        return self._environment.get_variable_type(node.value, node.context)

    def visit_unsignedint(self, node: Unsignedint) -> Type:
        return U8

    def visit_bool(self, node: Bool) -> Type:
        return BOOL
