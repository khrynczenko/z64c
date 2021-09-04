"""
Parser for the z64 language. It follows top-down approach using
recursive descent parsing.


Below is the language grammar.

<program> -> <statement>* EOF
<statement> -> <simple_statement> NEWLINE
<statement> -> <compount_statement> NEWLINE
<simple_statement> -> <print>
<simple_statement> -> <assignment>
<compound_statement> -> <if>
<if> -> IF <expression> COLON NEWLINE <block>
<block> INDENT <statement>* DEDENT
<print> -> PRINT LEFT_PAREN <expression> RIGHT_PAREN
<assignment> -> IDENTIFIER ASSIGN <expression>
<expression> -> <term> (PLUS <term>)*
<term> -> <factor> (STAR <factor>)*
<factor> -> PLUS <factor>
<factor> -> MINUS <factor>
<factor> -> LEFT_PAREN <expr> RIGHT_PAREN
<factor> -> <atom>
<atom> -> UNSIGNEDINT
<atom> -> IDENTIFIER
<atom> -> TRUE | FALSE
"""
from __future__ import annotations

import abc
from abc import ABC
from typing import List

from zx64c.scanner import Token, TokenCategory
from zx64c.ast import (
    SourceContext,
    Ast,
    Program,
    Block,
    If,
    Print,
    Assignment,
    Addition,
    Negation,
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


class UnexpectedToken(ParseError):
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
            raise UnexpectedToken([category], self._current_token.category, context)

        token = self._current_token
        self._tokens = self._tokens[1:]
        return token

    def _make_context(self) -> SourceContext:
        return SourceContext(self._current_token.line, self._current_token.column)

    def _parse_program(self) -> Ast:
        statements = []
        context = self._make_context()
        while self._current_token.category is not TokenCategory.EOF:
            statements.append(self._parse_statement())
        return Program(statements, context)

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
        elif categories[:2] == [TokenCategory.IDENTIFIER, TokenCategory.ASSIGN]:
            assignment_statement = self._parse_assignment()
            self._consume(TokenCategory.NEWLINE)
            return assignment_statement
        else:
            expression = self._parse_expression()
            self._consume(TokenCategory.NEWLINE)
            return expression

    def _parse_compound_statement(self) -> Ast:
        if_statement = self._parse_if()
        self._consume(TokenCategory.NEWLINE)
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

    def _parse_assignment(self) -> Ast:
        context = self._make_context()
        name_token = self._consume(TokenCategory.IDENTIFIER)
        self._consume(TokenCategory.ASSIGN)
        expression = self._parse_expression()
        return Assignment(name_token.lexeme, expression, context)

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
        if self._current_token.category is TokenCategory.UNSIGNEDINT:
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
            raise UnexpectedToken(
                [TokenCategory.UNSIGNEDINT, TokenCategory.IDENTIFIER],
                self._current_token.category,
                context,
            )
