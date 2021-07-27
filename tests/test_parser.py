from typing import List

from z64c.ast import (
    Program,
    Print,
    Assignment,
    Addition,
    Negation,
    Unsignedint,
    Identifier,
)
from z64c.scanner import Token, TokenCategory
from z64c.parser import Parser


def build_test_tokens_from_categories(categories: List[TokenCategory]):
    return [Token(0, 0, category, "") for category in categories]


def make_token_with_lexeme(category: TokenCategory, lexeme: str) -> Token:
    return Token(0, 0, category, lexeme)


def make_arbitrary_token(category: TokenCategory) -> Token:
    return Token(0, 0, category, "")


def test_parsing_print_identifier():
    tokens = [
        make_arbitrary_token(TokenCategory.PRINT),
        make_arbitrary_token(TokenCategory.LEFT_PAREN),
        make_token_with_lexeme(TokenCategory.UNSIGNEDINT, "10"),
        make_arbitrary_token(TokenCategory.RIGHT_PAREN),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.EOF),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = Program([Print(Unsignedint(10))])
    assert ast == expected_ast


def test_parsing_assignment_unsignedint():
    tokens = [
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "x"),
        make_arbitrary_token(TokenCategory.ASSIGN),
        make_token_with_lexeme(TokenCategory.UNSIGNEDINT, "10"),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.EOF),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = Program([Assignment("x", Unsignedint(10))])
    assert ast == expected_ast


def test_parsing_assignment_negated_unsignedint():
    tokens = [
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "x"),
        make_arbitrary_token(TokenCategory.ASSIGN),
        make_arbitrary_token(TokenCategory.MINUS),
        make_token_with_lexeme(TokenCategory.UNSIGNEDINT, "10"),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.EOF),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = Program([Assignment("x", Negation(Unsignedint(10)))])
    assert ast == expected_ast


def test_parsing_assignment_identifier():
    tokens = [
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "x"),
        make_arbitrary_token(TokenCategory.ASSIGN),
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "y"),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.EOF),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = Program([Assignment("x", Identifier("y"))])
    assert ast == expected_ast


def test_parsing_assignment_arithmetic_expression():
    tokens = [
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "x"),
        make_arbitrary_token(TokenCategory.ASSIGN),
        make_token_with_lexeme(TokenCategory.UNSIGNEDINT, "10"),
        make_arbitrary_token(TokenCategory.PLUS),
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "y"),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.EOF),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = Program(
        [Assignment("x", Addition(Unsignedint(10), Identifier("y")))]
    )
    assert ast == expected_ast


def test_parsing_assignment_complex_arithmetic_expression():
    tokens = [
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "x"),
        make_arbitrary_token(TokenCategory.ASSIGN),
        make_token_with_lexeme(TokenCategory.UNSIGNEDINT, "10"),
        make_arbitrary_token(TokenCategory.PLUS),
        make_arbitrary_token(TokenCategory.LEFT_PAREN),
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "y"),
        make_arbitrary_token(TokenCategory.PLUS),
        make_token_with_lexeme(TokenCategory.UNSIGNEDINT, "20"),
        make_arbitrary_token(TokenCategory.RIGHT_PAREN),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.EOF),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = Program(
        [
            Assignment(
                "x",
                Addition(Unsignedint(10), Addition(Identifier("y"), Unsignedint(20))),
            )
        ]
    )
    assert ast == expected_ast
