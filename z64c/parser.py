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


class Parser:
    def __init__(self, tokens: List[Token]):
        self._tokens = tokens

    def parse(self):
        self._parse_program()

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

    def _parse_program(self):
        while self._current_token.category is not TokenCategory.EOF:
            self._parse_statement()

    def _parse_statement(self):
        if self._current_token.category is TokenCategory.PRINT:
            self._parse_print()
        else:
            self._parse_assignment()
        self._consume(TokenCategory.NEWLINE)

    def _parse_print(self):
        self._consume(TokenCategory.PRINT)
        self._consume(TokenCategory.LEFT_PAREN)
        self._parse_expression()
        self._consume(TokenCategory.RIGHT_PAREN)

    def _parse_assignment(self):
        self._consume(TokenCategory.IDENTIFIER)
        self._consume(TokenCategory.ASSIGN)
        self._parse_expression()

    def _parse_expression(self):
        self._parse_term()
        while self._current_token.category is TokenCategory.PLUS:
            self._advance()
            self._parse_term()

    def _parse_term(self):
        self._parse_factor()
        while self._current_token.category is TokenCategory.STAR:
            self._advance()
            self._parse_factor()

    def _parse_factor(self):
        if self._current_token.category is TokenCategory.PLUS:
            self._advance()
            self._parse_factor()
        elif self._current_token.category is TokenCategory.MINUS:
            self._advance()
            self._parse_factor()
        elif self._current_token.category is TokenCategory.LEFT_PAREN:
            self._advance()
            self._parse_expression()
            self._consume(TokenCategory.RIGHT_PAREN)
        else:
            self._parse_atom()

    def _parse_atom(self):
        if self._current_token.category is TokenCategory.UNSIGNEDINT:
            self._advance()
        elif self._current_token.category is TokenCategory.IDENTIFIER:
            self._advance()
        else:
            raise RuntimeError(
                f"Unexpected token, expected one of "
                f"{[TokenCategory.UNSIGNEDINT, TokenCategory.IDENTIFIER]} got "
                f"{self._current_token.category}."
            )
