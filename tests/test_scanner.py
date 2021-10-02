import pytest

from zx64c.scanner import (
    Scanner,
    UnrecognizedTokenError,
    UnevenIndentError,
    Token,
    TokenCategory,
)


def test_scanner_raises_unrecognized_token_error():
    source = "?"
    scanner = Scanner(source)

    with pytest.raises(UnrecognizedTokenError):
        scanner.scan()


def test_scanner_produces_newline():
    source = "\n"
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 1, TokenCategory.NEWLINE, "\n"),
        Token(2, 1, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_token_after_a_newline():
    source = "\n123"
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 1, TokenCategory.NEWLINE, "\n"),
        Token(2, 1, TokenCategory.UNSIGNEDINT, "123"),
        Token(2, 4, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_left_paren():
    source = "  (  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.LEFT_PAREN, "("),
        Token(1, 6, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_right_paren():
    source = "  )  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.RIGHT_PAREN, ")"),
        Token(1, 6, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_left_bracket():
    source = "  [  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.LEFT_BRACKET, "["),
        Token(1, 6, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_right_bracket():
    source = "  ]  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.RIGHT_BRACKET, "]"),
        Token(1, 6, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_plus():
    source = "  +  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.PLUS, "+"),
        Token(1, 6, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_minus():
    source = "  -  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.MINUS, "-"),
        Token(1, 6, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_equal():
    source = "  ==  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.EQUAL, "=="),
        Token(1, 7, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_assign():
    source = "  =  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.ASSIGN, "="),
        Token(1, 6, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_colon():
    source = "  :  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.COLON, ":"),
        Token(1, 6, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_comma():
    source = "  ,  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.COMMA, ","),
        Token(1, 6, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_arrow():
    source = "  ->  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.ARROW, "->"),
        Token(1, 7, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_unsignedint():
    source = "  123  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.UNSIGNEDINT, "123"),
        Token(1, 8, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_def_keyword():
    source = "  def  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.DEF, "def"),
        Token(1, 8, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_return_keyword():
    source = "  return  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.RETURN, "return"),
        Token(1, 11, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_print_keyword():
    source = "  print  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.PRINT, "print"),
        Token(1, 10, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_true_keyword():
    source = "  true  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.TRUE, "true"),
        Token(1, 9, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_false_keyword():
    source = "  false  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.FALSE, "false"),
        Token(1, 10, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_identifier():
    source = "  _identifier_  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.IDENTIFIER, "_identifier_"),
        Token(1, 17, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_void():
    source = "  void  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.VOID, "void"),
        Token(1, 9, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_bool():
    source = "  bool  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.BOOL, "bool"),
        Token(1, 9, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_u8():
    source = "  u8  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.U8, "u8"),
        Token(1, 7, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_let():
    source = "  let  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.LET, "let"),
        Token(1, 8, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_if():
    source = "  if  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.IF, "if"),
        Token(1, 7, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_binary_addition():
    source = "  12 + 34"
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.UNSIGNEDINT, "12"),
        Token(1, 6, TokenCategory.PLUS, "+"),
        Token(1, 8, TokenCategory.UNSIGNEDINT, "34"),
        Token(1, 10, TokenCategory.EOF, ""),
    ]


def test_scanner_has_right_token_locations_for_two_line_program():
    source = "x = 1\nprint(1 + y)"
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 1, TokenCategory.IDENTIFIER, "x"),
        Token(1, 3, TokenCategory.ASSIGN, "="),
        Token(1, 5, TokenCategory.UNSIGNEDINT, "1"),
        Token(1, 6, TokenCategory.NEWLINE, "\n"),
        Token(2, 1, TokenCategory.PRINT, "print"),
        Token(2, 6, TokenCategory.LEFT_PAREN, "("),
        Token(2, 7, TokenCategory.UNSIGNEDINT, "1"),
        Token(2, 9, TokenCategory.PLUS, "+"),
        Token(2, 11, TokenCategory.IDENTIFIER, "y"),
        Token(2, 12, TokenCategory.RIGHT_PAREN, ")"),
        Token(2, 13, TokenCategory.EOF, ""),
    ]


def test_scanner_idents_and_dedents():
    source = "\n    1\n"
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 1, TokenCategory.NEWLINE, "\n"),
        Token(2, 1, TokenCategory.INDENT, "    "),
        Token(2, 5, TokenCategory.UNSIGNEDINT, "1"),
        Token(2, 6, TokenCategory.NEWLINE, "\n"),
        Token(3, 1, TokenCategory.DEDENT, "    "),
        Token(3, 1, TokenCategory.EOF, ""),
    ]


def test_scanner_with_nested_idents_and_dedents():
    source = "\n    1\n        1\n"
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 1, TokenCategory.NEWLINE, "\n"),
        Token(2, 1, TokenCategory.INDENT, "    "),
        Token(2, 5, TokenCategory.UNSIGNEDINT, "1"),
        Token(2, 6, TokenCategory.NEWLINE, "\n"),
        Token(3, 1, TokenCategory.INDENT, "    "),
        Token(3, 9, TokenCategory.UNSIGNEDINT, "1"),
        Token(3, 10, TokenCategory.NEWLINE, "\n"),
        Token(4, 1, TokenCategory.DEDENT, "    "),
        Token(4, 1, TokenCategory.DEDENT, "    "),
        Token(4, 1, TokenCategory.EOF, ""),
    ]


def test_scanner_with_nested_indents_and_nested_dedents():
    source = "\n    1\n        1\n    \n"
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 1, TokenCategory.NEWLINE, "\n"),
        Token(2, 1, TokenCategory.INDENT, "    "),
        Token(2, 5, TokenCategory.UNSIGNEDINT, "1"),
        Token(2, 6, TokenCategory.NEWLINE, "\n"),
        Token(3, 1, TokenCategory.INDENT, "    "),
        Token(3, 9, TokenCategory.UNSIGNEDINT, "1"),
        Token(4, 5, TokenCategory.NEWLINE, "\n"),
        Token(5, 1, TokenCategory.DEDENT, "    "),
        Token(5, 1, TokenCategory.DEDENT, "    "),
        Token(5, 1, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_error_on_uneven_indentation():
    source = "\n  1\n"
    scanner = Scanner(source)

    with pytest.raises(UnevenIndentError):
        scanner.scan()
