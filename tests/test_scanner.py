from zx64c.scanner import Scanner, Token, TokenCategory


def test_scanner_produces_newline():
    source = "  \n  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.NEWLINE, "\n"),
        Token(2, 3, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_token_after_a_newline():
    source = "  \n123"
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.NEWLINE, "\n"),
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


def test_scanner_produces_unsignedint():
    source = "  123  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.UNSIGNEDINT, "123"),
        Token(1, 8, TokenCategory.EOF, ""),
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
