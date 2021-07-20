from typing import List

from z64c.scanner import Token, TokenCategory
from z64c.parser import Parser


def build_test_tokens_from_categories(categories: List[TokenCategory]):
    return [Token(0, 0, category, "") for category in categories]


def test_parsing_print_identifier():
    tokens = build_test_tokens_from_categories(
        [
            TokenCategory.PRINT,
            TokenCategory.LEFT_PAREN,
            TokenCategory.UNSIGNEDINT,
            TokenCategory.RIGHT_PAREN,
            TokenCategory.NEWLINE,
            TokenCategory.EOF,
        ]
    )
    parser = Parser(tokens)
    parser.parse()


def test_parsing_assignment_unsignedint():
    tokens = build_test_tokens_from_categories(
        [
            TokenCategory.IDENTIFIER,
            TokenCategory.ASSIGN,
            TokenCategory.UNSIGNEDINT,
            TokenCategory.NEWLINE,
            TokenCategory.EOF,
        ]
    )
    parser = Parser(tokens)
    parser.parse()


def test_parsing_assignment_identifier():
    tokens = build_test_tokens_from_categories(
        [
            TokenCategory.IDENTIFIER,
            TokenCategory.ASSIGN,
            TokenCategory.IDENTIFIER,
            TokenCategory.NEWLINE,
            TokenCategory.EOF,
        ]
    )
    parser = Parser(tokens)
    parser.parse()


def test_parsing_assignment_arithmetic_expression():
    tokens = build_test_tokens_from_categories(
        [
            TokenCategory.IDENTIFIER,
            TokenCategory.ASSIGN,
            TokenCategory.UNSIGNEDINT,
            TokenCategory.STAR,
            TokenCategory.IDENTIFIER,
            TokenCategory.NEWLINE,
            TokenCategory.EOF,
        ]
    )
    parser = Parser(tokens)
    parser.parse()


def test_parsing_assignment_complex_arithmetic_expression():
    tokens = build_test_tokens_from_categories(
        [
            TokenCategory.IDENTIFIER,
            TokenCategory.ASSIGN,
            TokenCategory.UNSIGNEDINT,
            TokenCategory.STAR,
            TokenCategory.LEFT_PAREN,
            TokenCategory.IDENTIFIER,
            TokenCategory.PLUS,
            TokenCategory.UNSIGNEDINT,
            TokenCategory.RIGHT_PAREN,
            TokenCategory.NEWLINE,
            TokenCategory.EOF,
        ]
    )
    parser = Parser(tokens)
    parser.parse()
