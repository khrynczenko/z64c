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
<atom> -> TRUE | FALSE
"""

from typing import List

from z64c.scanner import Token, TokenCategory
from z64c.ast import (
    SourceContext,
    Ast,
    Program,
    Print,
    Assignment,
    Addition,
    Negation,
    Unsignedint,
    Identifier,
    Bool,
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

    def _make_context(self) -> SourceContext:
        return SourceContext(self._current_token.line, self._current_token.column)

    def _parse_program(self) -> Ast:
        statements = []
        context = self._make_context()
        while self._current_token.category is not TokenCategory.EOF:
            statements.append(self._parse_statement())
        return Program(statements, context)

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
        if self._current_token.category is TokenCategory.UNSIGNEDINT:
            value = int(self._current_token.lexeme)
            context = self._make_context()
            self._advance()
            return Unsignedint(value, context)
        elif self._current_token.category is TokenCategory.IDENTIFIER:
            value = self._current_token.lexeme
            context = self._make_context()
            self._advance()
            return Identifier(value, context)
        elif self._current_token.category in [TokenCategory.TRUE, TokenCategory.FALSE]:
            value = self._current_token.category is TokenCategory.TRUE
            context = self._make_context()
            self._advance()
            return Bool(value, context)
        else:
            raise RuntimeError(
                f"Unexpected token, expected one of "
                f"{[TokenCategory.UNSIGNEDINT, TokenCategory.IDENTIFIER]} got "
                f"{self._current_token.category}."
            )
