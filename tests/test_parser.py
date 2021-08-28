from typing import List

from tests.ast import (
    ProgramTC,
    PrintTC,
    AssignmentTC,
    AdditionTC,
    NegationTC,
    UnsignedintTC,
    IdentifierTC,
    BoolTC,
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
    expected_ast = ProgramTC([PrintTC(UnsignedintTC(10))])
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
    expected_ast = ProgramTC([AssignmentTC("x", UnsignedintTC(10))])
    assert ast == expected_ast


def test_parsing_assignment_bool_true():
    tokens = [
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "x"),
        make_arbitrary_token(TokenCategory.ASSIGN),
        make_arbitrary_token(TokenCategory.TRUE),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.EOF),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = ProgramTC([AssignmentTC("x", BoolTC(True))])
    assert ast == expected_ast


def test_parsing_assignment_bool_false():
    tokens = [
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "x"),
        make_arbitrary_token(TokenCategory.ASSIGN),
        make_arbitrary_token(TokenCategory.FALSE),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.EOF),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = ProgramTC([AssignmentTC("x", BoolTC(False))])
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
    expected_ast = ProgramTC([AssignmentTC("x", NegationTC(UnsignedintTC(10)))])
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
    expected_ast = ProgramTC([AssignmentTC("x", IdentifierTC("y"))])
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
    expected_ast = ProgramTC(
        [AssignmentTC("x", AdditionTC(UnsignedintTC(10), IdentifierTC("y")))]
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
    expected_ast = ProgramTC(
        [
            AssignmentTC(
                "x",
                AdditionTC(
                    UnsignedintTC(10), AdditionTC(IdentifierTC("y"), UnsignedintTC(20))
                ),
            )
        ]
    )
    assert ast == expected_ast
