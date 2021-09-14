from typing import List

from tests.ast import (
    ProgramTC,
    BlockTC,
    IfTC,
    PrintTC,
    LetTC,
    AssignmentTC,
    AdditionTC,
    NegationTC,
    UnsignedintTC,
    IdentifierTC,
    BoolTC,
    TEST_CONTEXT,
)
from zx64c.scanner import Token, TokenCategory
from zx64c.parser import Parser, UnexpectedTokenError
from zx64c.types import Type


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


def test_parsing_let_unsigned_int():
    tokens = [
        make_arbitrary_token(TokenCategory.LET),
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "x"),
        make_arbitrary_token(TokenCategory.COLON),
        make_token_with_lexeme(TokenCategory.U8, "u8"),
        make_arbitrary_token(TokenCategory.ASSIGN),
        make_token_with_lexeme(TokenCategory.UNSIGNEDINT, "10"),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.EOF),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = ProgramTC([LetTC("x", Type("u8"), UnsignedintTC(10))])
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


def test_parsing_if_statement():
    tokens = [
        make_arbitrary_token(TokenCategory.IF),
        make_arbitrary_token(TokenCategory.TRUE),
        make_arbitrary_token(TokenCategory.COLON),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.INDENT),
        make_token_with_lexeme(TokenCategory.IDENTIFIER, "y"),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.DEDENT),
        make_arbitrary_token(TokenCategory.EOF),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    expected_ast = ProgramTC([IfTC(BoolTC(True), BlockTC([IdentifierTC("y")]))])
    assert ast == expected_ast


def test_parser_raises_on_unexpected_token():
    tokens = [
        make_arbitrary_token(TokenCategory.IF),
        make_arbitrary_token(TokenCategory.TRUE),
        make_arbitrary_token(TokenCategory.COLON),
        make_arbitrary_token(TokenCategory.NEWLINE),
        make_arbitrary_token(TokenCategory.IDENTIFIER),
    ]

    parser = Parser(tokens)
    try:
        parser.parse()
    except UnexpectedTokenError as e:
        assert e == UnexpectedTokenError(
            [TokenCategory.INDENT], TokenCategory.IDENTIFIER, TEST_CONTEXT
        )
        return

    assert False, "Expected exception not raised"
