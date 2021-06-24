import dataclasses
import enum
import itertools

from typing import Text, List


@enum.unique
class Category(enum.Enum):
    EOF = enum.auto()
    NEWLINE = enum.auto()

    LEFT_PAREN = enum.auto()
    RIGHT_PAREN = enum.auto()
    STAR = enum.auto()
    SLASH = enum.auto()
    PLUS = enum.auto()
    MINUS = enum.auto()
    EQUAL = enum.auto()

    UNSIGNEDINT = enum.auto()
    IDENTIFIER = enum.auto()


@dataclasses.dataclass
class Token:
    line: int
    column: int
    category: Category
    lexeme: str


class Tokenizer:
    def __init__(self, source: Text):
        self._source = source
        self._source_index = 0
        self._line = 1
        self._column = 1
        self._produced_tokens = []

    def tokenize(self) -> List[Token]:
        while self._source_index < len(self._source):
            next_character = self._source[self._source_index]

            if next_character == " ":
                self._advance()

            elif next_character == "\n":
                self._produced_tokens.append(self._consume_newline())

            elif next_character == "(":
                self._produced_tokens.append(self._consume_left_paren())

            elif next_character == ")":
                self._produced_tokens.append(self._consume_right_paren())

            elif next_character == "*":
                self._produced_tokens.append(self._consume_star())

            elif next_character == "/":
                self._produced_tokens.append(self._consume_slash())

            elif next_character == "+":
                self._produced_tokens.append(self._consume_plus())

            elif next_character == "-":
                self._produced_tokens.append(self._consume_minus())

            elif next_character == "=":
                self._produced_tokens.append(self._consume_equal())

            elif next_character.isdigit():
                self._produced_tokens.append(self._consume_integer())

            elif _is_identifier_character(next_character):
                self._produced_tokens.append(self._consume_identifier())

            else:
                raise RuntimeError(
                    f"Unrecognized syntax at line {self._line} "
                    "column {self._column}."
                )

        return self._produced_tokens

    def _advance(self):
        if self._source[self._source_index] == "\n":
            self._line += 1
            self._column = 0

        self._column += 1
        self._source_index += 1

    def _consume_newline(self):
        token = Token(self._line, self._column, Category.NEWLINE, "\n")
        self._advance()

        return token

    def _consume_left_paren(self):
        token = Token(self._line, self._column, Category.LEFT_PAREN, "(")
        self._advance()

        return token

    def _consume_right_paren(self):
        token = Token(self._line, self._column, Category.RIGHT_PAREN, ")")
        self._advance()

        return token

    def _consume_star(self):
        token = Token(self._line, self._column, Category.STAR, "*")
        self._advance()

        return token

    def _consume_slash(self):
        token = Token(self._line, self._column, Category.SLASH, "/")
        self._advance()

        return token

    def _consume_plus(self):
        token = Token(self._line, self._column, Category.PLUS, "+")
        self._advance()

        return token

    def _consume_minus(self):
        token = Token(self._line, self._column, Category.MINUS, "-")
        self._advance()

        return token

    def _consume_equal(self):
        token = Token(self._line, self._column, Category.EQUAL, "=")
        self._advance()

        return token

    def _consume_integer(self):
        integer = "".join(
            itertools.takewhile(
                lambda c: c.isdigit(), self._source[self._source_index :]
            )
        )

        token = Token(self._line, self._column, Category.UNSIGNEDINT, integer)

        self._column += len(integer)
        self._source_index += len(integer)
        return token

    def _consume_identifier(self):
        identifier = "".join(
            itertools.takewhile(
                lambda c: _is_identifier_character(c),
                self._source[self._source_index :],
            )
        )

        token = Token(self._line, self._column, Category.IDENTIFIER, identifier)

        self._column += len(identifier)
        self._source_index += len(identifier)
        return token


def _is_identifier_character(c: Text) -> bool:
    return (c.isalpha() and c.isascii()) or c == "_"
