"""
Parser for the z64 language. It follows top-down approach using
recursive descent parsing.


Below is the language grammar.

<program> -> NEWLINE? <program_statement>* EOF
<program_statement> -> <function>
<function> ->
    DEF IDENTIFIER LEFT_PAREN <params> RIGHT_PAREN ARROW <type> COLON NEWLINE <block>
<parameteres> -> (<parameter>)? ( COMMA <parameter>)*
<parameter> -> IDENTIFIER COLON <type>
<statement> -> <simple_statement> NEWLINE
<statement> -> <compound_statement>
<simple_statement> -> <print>
<simple_statement> -> <assignment>
<simple_statement> -> <let>
<simple_statement> -> <return>
<compound_statement> -> <if>
<if> -> IF <expression> COLON NEWLINE <block>
<block> INDENT <statement>* DEDENT
<print> -> PRINT LEFT_PAREN <expression> RIGHT_PAREN
<let> -> LET IDENTIFIER COLON <type> ASSIGN <expression>
<return> -> RETURN <expression>
<assignment> -> IDENTIFIER ASSIGN <expression>
<expression> -> <term> (PLUS <term>)*
<term> -> <factor> (STAR <factor>)*
<factor> -> PLUS <factor>
<factor> -> MINUS <factor>
<factor> -> LEFT_PAREN <expr> RIGHT_PAREN
<factor> -> <atom>
<atom> -> <function_call>
<atom> -> UNSIGNEDINT
<atom> -> IDENTIFIER
<atom> -> TRUE | FALSE
<type> -> U8 | BOOL | <function_type> | IDENTIFIER
<function_call> -> IDENTIFIER LEFT_PAREN <args> RIGHT_PAREN
<args> -> (<expression>)? ( COMMA <expression>)*
<function_type> ->
    IDENTIFIER LEFT_BRACKET LEFT_BRACKET
    <param_types> RIGHT_BRACKET COMMA <type> RIGHT_BRACKET
"""
from __future__ import annotations

import abc
from abc import ABC
from typing import List

from zx64c.scanner import Token, TokenCategory
from zx64c import types
from zx64c.ast import Parameter
from zx64c.ast import (
    SourceContext,
    Ast,
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
    FunctionCall,
    Unsignedint,
    Identifier,
    Bool,
)


class ParseError(Exception, ABC):
    def __init__(self, context: SourceContext):
        self._context = context

    def make_error_message(self) -> str:
        return (
            f"At line {self._context.line}, column {self._context.column}: "
            f"{self._make_error_message()}"
        )

    @abc.abstractmethod
    def _make_error_message(self) -> str:
        pass

    def __eq__(self, rhs: ParseError):
        return self.make_error_message() == rhs.make_error_message()


class UnexpectedTokenError(ParseError):
    def __init__(
        self,
        expected_tokens: [TokenCategory],
        encountered_token: TokenCategory,
        context: SourceContext,
    ):
        super().__init__(context)
        self._expected_tokens = expected_tokens
        self._encountered_token = encountered_token

    def _make_error_message(self) -> str:
        expected_tokens = "".join([str(tok) + ", " for tok in self._expected_tokens])
        expected_tokens = expected_tokens.rstrip(", ")
        return (
            f"Encountered unexpected token {self._encountered_token}. Expected "
            f"one of {expected_tokens}."
        )


class Parser:
    def __init__(self, tokens: List[Token]):
        self._tokens = tokens

    def parse(self):
        return self._parse_program()

    @property
    def _current_token(self) -> Token:
        return self._tokens[0]

    def _advance(self):
        self._tokens = self._tokens[1:]

    def _consume(self, category: TokenCategory) -> Token:
        if self._current_token.category is not category:
            context = self._make_context()
            raise UnexpectedTokenError(
                [category], self._current_token.category, context
            )

        token = self._current_token
        self._tokens = self._tokens[1:]
        return token

    def _make_context(self) -> SourceContext:
        return SourceContext(self._current_token.line, self._current_token.column)

    def _parse_program(self) -> Ast:
        functions = []
        context = self._make_context()
        if self._current_token.category is TokenCategory.NEWLINE:
            self._advance()
        while self._current_token.category is not TokenCategory.EOF:
            functions.append(self._parse_function())
        return Program(functions, context)

    def _parse_function(self) -> Parameter:
        context = self._make_context()
        self._consume(TokenCategory.DEF)
        identifier = self._consume(TokenCategory.IDENTIFIER)
        self._consume(TokenCategory.LEFT_PAREN)
        parameters = self._parse_parameters()
        self._consume(TokenCategory.RIGHT_PAREN)
        self._consume(TokenCategory.ARROW)
        return_type_id = self._parse_type()
        self._consume(TokenCategory.COLON)
        self._consume(TokenCategory.NEWLINE)
        block = self._parse_block()
        return Function(identifier.lexeme, parameters, return_type_id, block, context)

    def _parse_parameters(self) -> [Parameter]:
        if self._current_token.category is TokenCategory.RIGHT_PAREN:
            return []

        parameters = []
        parameters.append(self._parse_parameter())

        while self._current_token.category is TokenCategory.COMMA:
            self._advance()
            parameters.append(self._parse_parameter())

        return parameters

    def _parse_parameter(self) -> Parameter:
        identifier = self._consume(TokenCategory.IDENTIFIER)
        self._consume(TokenCategory.COLON)
        type_id = self._parse_type()
        return Parameter(identifier.lexeme, type_id)

    def _parse_statement(self) -> Ast:
        if self._current_token.category in [TokenCategory.IF]:
            return self._parse_compound_statement()
        else:
            return self._parse_simple_statement()

    def _parse_simple_statement(self) -> Ast:
        categories = [tok.category for tok in self._tokens]
        if self._current_token.category is TokenCategory.PRINT:
            print_statement = self._parse_print()
            self._consume(TokenCategory.NEWLINE)
            return print_statement
        elif categories[0] is TokenCategory.LET:
            let_statement = self._parse_let()
            self._consume(TokenCategory.NEWLINE)
            return let_statement
        elif categories[:2] == [TokenCategory.IDENTIFIER, TokenCategory.ASSIGN]:
            assignment_statement = self._parse_assignment()
            self._consume(TokenCategory.NEWLINE)
            return assignment_statement
        elif categories[0] is TokenCategory.RETURN:
            return_statement = self._parse_return()
            self._consume(TokenCategory.NEWLINE)
            return return_statement
        else:
            expression = self._parse_expression()
            self._consume(TokenCategory.NEWLINE)
            return expression

    def _parse_compound_statement(self) -> Ast:
        if_statement = self._parse_if()
        return if_statement

    def _parse_if(self) -> Ast:
        context = self._make_context()
        self._consume(TokenCategory.IF)
        condition = self._parse_expression()
        self._consume(TokenCategory.COLON)
        self._consume(TokenCategory.NEWLINE)
        consequence = self._parse_block()
        return If(condition, consequence, context)

    def _parse_block(self) -> Ast:
        context = self._make_context()
        statements = []
        self._consume(TokenCategory.INDENT)
        while self._current_token.category is not TokenCategory.DEDENT:
            statements.append(self._parse_statement())
        self._consume(TokenCategory.DEDENT)
        return Block(statements, context)

    def _parse_print(self) -> Ast:
        context = self._make_context()
        self._consume(TokenCategory.PRINT)
        self._consume(TokenCategory.LEFT_PAREN)
        expression = self._parse_expression()
        self._consume(TokenCategory.RIGHT_PAREN)
        return Print(expression, context)

    def _parse_let(self) -> Ast:
        context = self._make_context()
        self._consume(TokenCategory.LET)
        name_token = self._consume(TokenCategory.IDENTIFIER)
        self._consume(TokenCategory.COLON)
        type_name = self._parse_type()
        self._consume(TokenCategory.ASSIGN)
        expression = self._parse_expression()
        return Let(name_token.lexeme, type_name, expression, context)

    def _parse_assignment(self) -> Ast:
        context = self._make_context()
        name_token = self._consume(TokenCategory.IDENTIFIER)
        self._consume(TokenCategory.ASSIGN)
        expression = self._parse_expression()
        return Assignment(name_token.lexeme, expression, context)

    def _parse_return(self) -> Ast:
        context = self._make_context()
        self._consume(TokenCategory.RETURN)
        expression = self._parse_expression()
        return Return(expression, context)

    def _parse_expression(self) -> Ast:
        lhs = self._parse_term()
        if self._current_token.category is TokenCategory.PLUS:
            context = self._make_context()
            self._advance()
            rhs = self._parse_expression()
            return Addition(lhs, rhs, context)
        return lhs

    def _parse_term(self) -> Ast:
        return self._parse_factor()

    def _parse_factor(self) -> Ast:
        if self._current_token.category is TokenCategory.PLUS:
            self._advance()
            return self._parse_factor()
        elif self._current_token.category is TokenCategory.MINUS:
            context = self._make_context()
            self._advance()
            factor = self._parse_factor()
            return Negation(factor, context)
        elif self._current_token.category is TokenCategory.LEFT_PAREN:
            self._advance()
            expression = self._parse_expression()
            self._consume(TokenCategory.RIGHT_PAREN)
            return expression
        else:
            return self._parse_atom()

    def _parse_atom(self) -> Ast:
        context = self._make_context()
        next_token_categories = [tok.category for tok in self._tokens[:2]]
        if next_token_categories == [
            TokenCategory.IDENTIFIER,
            TokenCategory.LEFT_PAREN,
        ]:
            return self._parse_function_call()
        elif self._current_token.category is TokenCategory.UNSIGNEDINT:
            value = int(self._current_token.lexeme)
            self._advance()
            return Unsignedint(value, context)
        elif self._current_token.category is TokenCategory.IDENTIFIER:
            value = self._current_token.lexeme
            self._advance()
            return Identifier(value, context)
        elif self._current_token.category in [TokenCategory.TRUE, TokenCategory.FALSE]:
            value = self._current_token.category is TokenCategory.TRUE
            self._advance()
            return Bool(value, context)
        else:
            raise UnexpectedTokenError(
                [
                    TokenCategory.UNSIGNEDINT,
                    TokenCategory.TRUE,
                    TokenCategory.FALSE,
                    TokenCategory.IDENTIFIER,
                ],
                self._current_token.category,
                context,
            )

    def _parse_function_call(self) -> Ast:
        context = self._make_context()
        function_name = self._consume(TokenCategory.IDENTIFIER).lexeme
        self._consume(TokenCategory.LEFT_PAREN)
        arguments = []
        if self._current_token.category is not TokenCategory.RIGHT_PAREN:
            arguments.append(self._parse_expression())

        while self._current_token.category is not TokenCategory.RIGHT_PAREN:
            self._consume(TokenCategory.COMMA)
            arguments.append(self._parse_expression())

        self._consume(TokenCategory.RIGHT_PAREN)

        return FunctionCall(function_name, arguments, context)

    def _parse_type(self) -> types.Type:
        context = self._make_context()
        built_in_types = [
            TokenCategory.VOID,
            TokenCategory.BOOL,
            TokenCategory.I8,
            TokenCategory.U8,
        ]
        possible_type_tokens = [
            TokenCategory.IDENTIFIER,
        ]

        if self._current_token.category in built_in_types:
            to_type = {
                "bool": types.Bool(),
                "i8": types.I8(),
                "u8": types.U8(),
                "void": types.Void(),
            }
            value = self._current_token.lexeme
            self._advance()
            return to_type[value]
        elif (
            len(self._tokens) > 1
            and self._tokens[0].category is TokenCategory.IDENTIFIER
            and self._tokens[1].category is TokenCategory.LEFT_BRACKET
        ):
            return self._parse_function_type(self)
        elif self._current_token.category is TokenCategory.IDENTIFIER:
            name = self._consume(TokenCategory.IDENTIFIER).lexeme
            return types.TypeIdentifier(name)
        else:
            raise UnexpectedTokenError(
                possible_type_tokens,
                self._current_token.category,
                context,
            )

    def _parse_function_type(self) -> types.Type:
        self._consume(TokenCategory.LEFT_BRACKET)
        self._consume(TokenCategory.LEFT_BRACKET)
        param_types = self._parse_param_types(self)
        self._consume(TokenCategory.RIGHT_BRACKET)
        return_type = self._parse_type()
        self._consume(TokenCategory.RIGHT_PAREN)
        return types.Callable(return_type, param_types)

    def _parse_param_types(self) -> [types.Type]:
        if self._current_token.category is TokenCategory.RIGHT_BRACKET:
            return []

        parameter_types = []
        parameter_types.append(self._parse_type())

        while self._current_token.category is TokenCategory.COMMA:
            self._advance()
            parameter_types.append(self._parse_type())

        return parameter_types
