from z64c import lexer as lex


def test_tokenizer_produces_integer():
    source = "  123  "
    tokenizer = lex.Tokenizer(source)
    tokens = tokenizer.tokenize()

    assert tokens == [lex.Token(1, 3, lex.Category.INTEGER, "123")]


def test_tokenizer_produces_left_paren():
    source = "  (  "
    tokenizer = lex.Tokenizer(source)
    tokens = tokenizer.tokenize()

    assert tokens == [lex.Token(1, 3, lex.Category.LEFT_PAREN, "(")]


def test_tokenizer_produces_right_paren():
    source = "  )  "
    tokenizer = lex.Tokenizer(source)
    tokens = tokenizer.tokenize()

    assert tokens == [lex.Token(1, 3, lex.Category.RIGHT_PAREN, ")")]


def test_tokenizer_produces_star():
    source = "  *  "
    tokenizer = lex.Tokenizer(source)
    tokens = tokenizer.tokenize()

    assert tokens == [lex.Token(1, 3, lex.Category.STAR, "*")]


def test_tokenizer_produces_slash():
    source = "  /  "
    tokenizer = lex.Tokenizer(source)
    tokens = tokenizer.tokenize()

    assert tokens == [lex.Token(1, 3, lex.Category.SLASH, "/")]


def test_tokenizer_produces_plus():
    source = "  +  "
    tokenizer = lex.Tokenizer(source)
    tokens = tokenizer.tokenize()

    assert tokens == [lex.Token(1, 3, lex.Category.PLUS, "+")]


def test_tokenizer_produces_minus():
    source = "  -  "
    tokenizer = lex.Tokenizer(source)
    tokens = tokenizer.tokenize()

    assert tokens == [lex.Token(1, 3, lex.Category.MINUS, "-")]


def test_tokenizer_produces_equal():
    source = "  =  "
    tokenizer = lex.Tokenizer(source)
    tokens = tokenizer.tokenize()

    assert tokens == [lex.Token(1, 3, lex.Category.EQUAL, "=")]


def test_tokenizer_produces_newline():
    source = "  \n  "
    tokenizer = lex.Tokenizer(source)
    tokens = tokenizer.tokenize()

    assert tokens == [lex.Token(1, 3, lex.Category.NEWLINE, "\n")]


def test_tokenizer_produces_token_after_a_newline():
    source = "  \n123"
    tokenizer = lex.Tokenizer(source)
    tokens = tokenizer.tokenize()

    assert tokens == [
        lex.Token(1, 3, lex.Category.NEWLINE, "\n"),
        lex.Token(2, 1, lex.Category.INTEGER, "123"),
    ]


def test_tokenizer_produces_binary_addition():
    source = "  12 + 34"
    tokenizer = lex.Tokenizer(source)
    tokens = tokenizer.tokenize()

    assert tokens == [
        lex.Token(1, 3, lex.Category.INTEGER, "12"),
        lex.Token(1, 6, lex.Category.PLUS, "+"),
        lex.Token(1, 8, lex.Category.INTEGER, "34"),
    ]
