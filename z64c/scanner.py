"""
This file forms a lexical specification and its implemetation for the
z64 language.

"""
import dataclasses
import enum
import itertools

from typing import Text, List, Callable


@enum.unique
class TokenCategory(enum.Enum):
    # SIGNIFICANT WHITESPACE
    EOF = enum.auto()
    NEWLINE = enum.auto()

    # KEYWORDS
    PRINT = enum.auto()

    # OPERATORS
    LEFT_PAREN = enum.auto()
    RIGHT_PAREN = enum.auto()
    STAR = enum.auto()
    SLASH = enum.auto()
    PLUS = enum.auto()
    MINUS = enum.auto()
    EQUAL = enum.auto()

    # LITERALS
    UNSIGNEDINT = enum.auto()
    IDENTIFIER = enum.auto()


KEYWORD_CATEGORIES = {"print": TokenCategory.PRINT}


@dataclasses.dataclass
class Token:
    line: int
    column: int
    category: TokenCategory
    lexeme: str


class Scanner:
    def __init__(self, source: Text):
        self._source = source
        self._source_index = 0
        self._line = 1
        self._column = 1
        self._produced_tokens = []

    def scan(self) -> List[Token]:
        while self._source_index < len(self._source):
            next_character = self._source[self._source_index]

            if next_character == " ":
                self._advance()

            elif next_character == "\n":
                self._produced_tokens.append(
                    self._consume_one_character_symbol("\n", TokenCategory.NEWLINE)
                )

            elif next_character == "(":
                self._produced_tokens.append(
                    self._consume_one_character_symbol("(", TokenCategory.LEFT_PAREN)
                )

            elif next_character == ")":
                self._produced_tokens.append(
                    self._consume_one_character_symbol(")", TokenCategory.RIGHT_PAREN)
                )

            elif next_character == "*":
                self._produced_tokens.append(
                    self._consume_one_character_symbol("*", TokenCategory.STAR)
                )

            elif next_character == "/":
                self._produced_tokens.append(
                    self._consume_one_character_symbol("/", TokenCategory.SLASH)
                )

            elif next_character == "+":
                self._produced_tokens.append(
                    self._consume_one_character_symbol("+", TokenCategory.PLUS)
                )

            elif next_character == "-":
                self._produced_tokens.append(
                    self._consume_one_character_symbol("-", TokenCategory.MINUS)
                )

            elif next_character == "=":
                self._produced_tokens.append(
                    self._consume_one_character_symbol("=", TokenCategory.EQUAL)
                )

            elif next_character.isdigit():
                self._produced_tokens.append(
                    self._consume_multi_character_symbol(
                        str.isdigit, TokenCategory.UNSIGNEDINT
                    )
                )

            elif self._is_keyword_next():
                self._produced_tokens.append(
                    self._consume_keyword(_is_identifier_character)
                )

            elif _is_identifier_character(next_character):
                self._produced_tokens.append(
                    self._consume_multi_character_symbol(
                        _is_identifier_character, TokenCategory.IDENTIFIER
                    )
                )

            else:
                raise RuntimeError(
                    f"Unrecognized syntax at line {self._line} "
                    "column {self._column}."
                )

        return self._produced_tokens + [
            Token(self._line, self._column, TokenCategory.EOF, "")
        ]

    def _is_keyword_next(self):
        return any(
            map(
                lambda keyword: self._source[self._source_index :].startswith(keyword),
                KEYWORD_CATEGORIES,
            )
        )

    def _advance(self):
        if self._source[self._source_index] == "\n":
            self._line += 1
            self._column = 0

        self._column += 1
        self._source_index += 1

    def _consume_one_character_symbol(self, character: str, category: TokenCategory):
        token = Token(self._line, self._column, category, character)
        self._advance()

        return token

    def _consume_keyword(
        self,
        character_predicate: Callable[[str], bool],
    ):
        characters = "".join(
            itertools.takewhile(character_predicate, self._source[self._source_index :])
        )

        token = Token(
            self._line, self._column, KEYWORD_CATEGORIES[characters], characters
        )

        self._column += len(characters)
        self._source_index += len(characters)

        return token

    def _consume_multi_character_symbol(
        self,
        character_predicate: Callable[[str], bool],
        resulting_category: TokenCategory,
    ):
        characters = "".join(
            itertools.takewhile(character_predicate, self._source[self._source_index :])
        )

        token = Token(self._line, self._column, resulting_category, characters)

        self._column += len(characters)
        self._source_index += len(characters)

        return token


def _is_identifier_character(c: Text) -> bool:
    return (c.isalpha() and c.isascii()) or c == "_"
