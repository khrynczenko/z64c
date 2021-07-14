from z64c.scanner import Scanner, Token, TokenCategory


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


def test_scanner_produces_star():
    source = "  *  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.STAR, "*"),
        Token(1, 6, TokenCategory.EOF, ""),
    ]


def test_scanner_produces_slash():
    source = "  /  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.SLASH, "/"),
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
    source = "  =  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.EQUAL, "="),
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
