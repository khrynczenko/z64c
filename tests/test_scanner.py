from z64c.scanner import Scanner, Token, TokenCategory


def test_scanner_produces_newline():
    source = "  \n  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [Token(1, 3, TokenCategory.NEWLINE, "\n")]


def test_scanner_produces_token_after_a_newline():
    source = "  \n123"
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.NEWLINE, "\n"),
        Token(2, 1, TokenCategory.UNSIGNEDINT, "123"),
    ]


def test_scanner_produces_left_paren():
    source = "  (  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [Token(1, 3, TokenCategory.LEFT_PAREN, "(")]


def test_scanner_produces_right_paren():
    source = "  )  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [Token(1, 3, TokenCategory.RIGHT_PAREN, ")")]


def test_scanner_produces_star():
    source = "  *  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [Token(1, 3, TokenCategory.STAR, "*")]


def test_scanner_produces_slash():
    source = "  /  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [Token(1, 3, TokenCategory.SLASH, "/")]


def test_scanner_produces_plus():
    source = "  +  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [Token(1, 3, TokenCategory.PLUS, "+")]


def test_scanner_produces_minus():
    source = "  -  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [Token(1, 3, TokenCategory.MINUS, "-")]


def test_scanner_produces_equal():
    source = "  =  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [Token(1, 3, TokenCategory.EQUAL, "=")]


def test_scanner_produces_unsignedint():
    source = "  123  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [Token(1, 3, TokenCategory.UNSIGNEDINT, "123")]


def test_scanner_produces_identifier():
    source = "  _identifier_  "
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [Token(1, 3, TokenCategory.IDENTIFIER, "_identifier_")]


def test_scanner_produces_binary_addition():
    source = "  12 + 34"
    scanner = Scanner(source)
    tokens = scanner.scan()

    assert tokens == [
        Token(1, 3, TokenCategory.UNSIGNEDINT, "12"),
        Token(1, 6, TokenCategory.PLUS, "+"),
        Token(1, 8, TokenCategory.UNSIGNEDINT, "34"),
    ]
