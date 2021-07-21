"""
Parser for the z64 language. It follows top-down approach using
recursive descent parsing.


Below is the language grammar.

<program> -> <statement>* EOF
<statement> -> <simple_statement> NEWLINE
<simple_statement> -> <print>
<simple_statement> -> <assignment>
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
"""

from typing import List

from z64c.scanner import Token, TokenCategory
from z64c.ast import (
    Ast,
    Program,
    Print,
    Assignment,
    Addition,
    Multiplication,
    Negation,
    Unsignedint,
    Identifier,
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
            raise RuntimeError(
                f"Unexpected token, expected {category} got "
                f"{self._current_token.category}."
            )
        token = self._current_token
        self._tokens = self._tokens[1:]
        return token

    def _parse_program(self) -> Ast:
        statements = []
        while self._current_token.category is not TokenCategory.EOF:
            statements.append(self._parse_statement())
        return Program(statements)

    def _parse_statement(self) -> Ast:
        if self._current_token.category is TokenCategory.PRINT:
            print_statement = self._parse_print()
            self._consume(TokenCategory.NEWLINE)
            return print_statement
        else:
            assignment_statement = self._parse_assignment()
            self._consume(TokenCategory.NEWLINE)
            return assignment_statement

    def _parse_print(self) -> Ast:
        self._consume(TokenCategory.PRINT)
        self._consume(TokenCategory.LEFT_PAREN)
        expression = self._parse_expression()
        self._consume(TokenCategory.RIGHT_PAREN)
        return Print(expression)

    def _parse_assignment(self) -> Ast:
        name_token = self._consume(TokenCategory.IDENTIFIER)
        self._consume(TokenCategory.ASSIGN)
        expression = self._parse_expression()
        return Assignment(name_token.lexeme, expression)

    def _parse_expression(self) -> Ast:
        lhs = self._parse_term()
        if self._current_token.category is TokenCategory.PLUS:
            self._advance()
            rhs = self._parse_expression()
            return Addition(lhs, rhs)
        return lhs

    def _parse_term(self) -> Ast:
        lhs = self._parse_factor()
        if self._current_token.category is TokenCategory.STAR:
            self._advance()
            rhs = self._parse_term()
            return Multiplication(lhs, rhs)
        return lhs

    def _parse_factor(self) -> Ast:
        if self._current_token.category is TokenCategory.PLUS:
            self._advance()
            return self._parse_factor()
        elif self._current_token.category is TokenCategory.MINUS:
            self._advance()
            factor = self._parse_factor()
            return Negation(factor)
        elif self._current_token.category is TokenCategory.LEFT_PAREN:
            self._advance()
            expression = self._parse_expression()
            self._consume(TokenCategory.RIGHT_PAREN)
            return expression
        else:
            return self._parse_atom()

    def _parse_atom(self) -> Ast:
        if self._current_token.category is TokenCategory.UNSIGNEDINT:
            value = int(self._current_token.lexeme)
            self._advance()
            return Unsignedint(value)
        elif self._current_token.category is TokenCategory.IDENTIFIER:
            value = self._current_token.lexeme
            self._advance()
            return Identifier(value)
        else:
            raise RuntimeError(
                f"Unexpected token, expected one of "
                f"{[TokenCategory.UNSIGNEDINT, TokenCategory.IDENTIFIER]} got "
                f"{self._current_token.category}."
            )
