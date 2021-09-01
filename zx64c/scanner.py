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
    INDENT = enum.auto()
    DEDENT = enum.auto()

    # KEYWORDS
    PRINT = enum.auto()
    TRUE = enum.auto()
    FALSE = enum.auto()

    # PARENTHESES
    LEFT_PAREN = enum.auto()
    RIGHT_PAREN = enum.auto()

    # BINARY OP
    PLUS = enum.auto()
    MINUS = enum.auto()
    EQUAL = enum.auto()
    ASSIGN = enum.auto()

    # LITERALS
    UNSIGNEDINT = enum.auto()
    IDENTIFIER = enum.auto()


KEYWORD_CATEGORIES = {
    "print": TokenCategory.PRINT,
    "true": TokenCategory.TRUE,
    "false": TokenCategory.FALSE,
}


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
        self._indent_level = 0

    def scan(self) -> List[Token]:
        while self._source_index < len(self._source):
            remaining_source = self._source[self._source_index :]

            if remaining_source.startswith(" "):
                self._advance()

            elif remaining_source.startswith("\n"):
                self._produced_tokens.append(
                    self._consume_one_character_symbol("\n", TokenCategory.NEWLINE)
                )
                self._produced_tokens.extend(self._consume_possible_indentations())

            elif remaining_source.startswith("("):
                self._produced_tokens.append(
                    self._consume_one_character_symbol("(", TokenCategory.LEFT_PAREN)
                )

            elif remaining_source.startswith(")"):
                self._produced_tokens.append(
                    self._consume_one_character_symbol(")", TokenCategory.RIGHT_PAREN)
                )

            elif remaining_source.startswith("+"):
                self._produced_tokens.append(
                    self._consume_one_character_symbol("+", TokenCategory.PLUS)
                )

            elif remaining_source.startswith("-"):
                self._produced_tokens.append(
                    self._consume_one_character_symbol("-", TokenCategory.MINUS)
                )

            elif remaining_source.startswith("=="):
                self._produced_tokens.append(
                    self._consume_two_character_symbol("==", TokenCategory.EQUAL)
                )

            elif remaining_source.startswith("="):
                self._produced_tokens.append(
                    self._consume_one_character_symbol("=", TokenCategory.ASSIGN)
                )

            elif remaining_source[0].isdigit():
                self._produced_tokens.append(
                    self._consume_multi_character_symbol(
                        str.isdigit, TokenCategory.UNSIGNEDINT
                    )
                )

            elif self._is_keyword_next():
                self._produced_tokens.append(
                    self._consume_keyword(_is_identifier_character)
                )

            elif _is_identifier_character(remaining_source[0]):
                self._produced_tokens.append(
                    self._consume_multi_character_symbol(
                        _is_identifier_character, TokenCategory.IDENTIFIER
                    )
                )

            else:
                raise RuntimeError(
                    f"Unrecognized syntax at line {self._line} "
                    f"column {self._column}."
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

    def _advance_many(self, count):
        for i in range(count):
            self._advance()

    def _advance(self):
        if self._source[self._source_index] == "\n":
            self._line += 1
            self._column = 0

        self._column += 1
        self._source_index += 1

    def _consume_possible_indentations(self):
        indents = []
        new_indent_level = self._count_indentations()

        if self._indent_level < new_indent_level:
            # new indent level is higher so we add INDENT tokens
            for _ in range(new_indent_level - self._indent_level):
                indents.append(
                    Token(self._line, self._column, TokenCategory.INDENT, "    ")
                )
        else:
            for _ in range(self._indent_level - new_indent_level):
                # new indent level is lower so we add DEDENT tokens
                indents.append(
                    Token(self._line, self._column, TokenCategory.DEDENT, "    ")
                )

        self._advance_many(new_indent_level * 4)
        self._indent_level = new_indent_level
        return indents

    def _count_indentations(self):
        space_count = len(
            list(
                itertools.takewhile(
                    lambda s: s == " ", self._source[self._source_index :]
                )
            )
        )
        if space_count == 0:
            return 0

        if space_count % 4 != 0:
            raise RuntimeError(
                "The only whitespace that is allowed at the beginning of a line "
                "is one or more indentations and each must be made of four spaces."
                "Whitespace count at line {self._line} is {space_count} which "
                "is not a multiple of 4"
            )
        return space_count // 4

    def _consume_one_character_symbol(self, character: str, category: TokenCategory):
        token = Token(self._line, self._column, category, character)
        self._advance()

        return token

    def _consume_two_character_symbol(self, characters: str, category: TokenCategory):
        token = Token(self._line, self._column, category, characters)
        self._advance()
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
