"""
This file forms a lexical specification and its implemetation for the
z64 language.

"""
from __future__ import annotations

import abc
import dataclasses
import enum
import itertools

from abc import ABC
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
    BOOL = enum.auto()
    U8 = enum.auto()
    LET = enum.auto()
    IF = enum.auto()

    COLON = enum.auto()

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

    def __str__(self):
        str_map = {
            TokenCategory.EOF: "EOF",
            TokenCategory.NEWLINE: "\\n",
            TokenCategory.INDENT: "INDENT",
            TokenCategory.DEDENT: "DEDENT",
            TokenCategory.PRINT: "print",
            TokenCategory.TRUE: "true",
            TokenCategory.FALSE: "false",
            TokenCategory.BOOL: "bool",
            TokenCategory.U8: "u8",
            TokenCategory.LET: "let",
            TokenCategory.IF: "if",
            TokenCategory.COLON: ":",
            TokenCategory.LEFT_PAREN: "(",
            TokenCategory.RIGHT_PAREN: ")",
            TokenCategory.PLUS: "+",
            TokenCategory.MINUS: "-",
            TokenCategory.EQUAL: "==",
            TokenCategory.ASSIGN: "=",
            TokenCategory.UNSIGNEDINT: "<decimal>",
            TokenCategory.IDENTIFIER: "<identifier>",
        }
        return f"'{str_map[self]}'"


KEYWORD_CATEGORIES = {
    "print": TokenCategory.PRINT,
    "true": TokenCategory.TRUE,
    "false": TokenCategory.FALSE,
    "bool": TokenCategory.BOOL,
    "u8": TokenCategory.U8,
    "let": TokenCategory.LET,
    "if": TokenCategory.IF,
}


class ScanError(Exception, ABC):
    def __init__(self, line: int, column: int):
        self._line = line
        self._column = column

    def make_error_message(self) -> str:
        return (
            f"At line {self._line}, column {self._column}: {self._make_error_message()}"
        )

    @abc.abstractmethod
    def _make_error_message(self) -> str:
        pass

    @abc.abstractmethod
    def __eq__(self, rhs: ScanError) -> bool:
        pass


class UnrecognizedTokenError(ScanError):
    def __init__(self, line: int, column: int, leading_char: str):
        super().__init__(line, column)
        self._leading_char = leading_char

    def _make_error_message(self) -> str:
        return (
            f"Unrecognized syntax. There is no valid tokens that starts"
            f"with `{self._leading_char}`."
        )

    def __eq__(self, rhs: UnrecognizedTokenError) -> bool:
        return (self._line, self._column) == (rhs._line, rhs._column)


class UnevenIndentError(ScanError):
    def __init__(self, line: int, column: int, space_count: int):
        super().__init__(line, column)
        self._space_count = space_count

    def _make_error_message(self) -> str:
        return (
            "The only whitespace that is allowed at the beginning of a line "
            "is one or more indentations and each must be made of four spaces. "
            f"Whitespace count at this line is {self._space_count} which "
            f"is not a multiple of 4."
        )

    def __eq__(self, rhs: UnevenIndentError) -> bool:
        return (self._line, self._column, self._space_count) == (
            rhs._line,
            rhs._column,
            self._space_count,
        )


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
            remaining_source = self._remaining_source

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

            elif remaining_source.startswith(":"):
                self._produced_tokens.append(
                    self._consume_one_character_symbol(":", TokenCategory.COLON)
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

            elif _is_identifier_leading_character(remaining_source[0]):
                self._produced_tokens.append(
                    self._consume_multi_character_symbol(
                        _is_identifier_character, TokenCategory.IDENTIFIER
                    )
                )

            else:
                raise UnrecognizedTokenError(
                    self._line, self._column, self._source[self._source_index]
                )

        return self._remove_extra_newlines(
            self._produced_tokens
            + [Token(self._line, self._column, TokenCategory.EOF, "")]
        )

    @property
    def _remaining_source(self):
        return self._source[self._source_index :]

    def _remove_extra_newlines(self, tokens: [Token]):
        filtered_tokens = []

        tokens_shifted_right = itertools.cycle(tokens)
        next(tokens_shifted_right)
        # ^ we obtained second iterator to tokens but shifted to right by one
        #   thanks to that we can now iterator over both of them and
        #   have easy access to current token and next token each iteration

        for token, next_token in zip(tokens, tokens_shifted_right):
            if (
                token.category is TokenCategory.NEWLINE
                and next_token.category is TokenCategory.NEWLINE
            ):
                continue
            filtered_tokens.append(token)
        return filtered_tokens

    def _is_keyword_next(self):
        return any(
            map(
                lambda keyword: self._remaining_source.startswith(keyword),
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
        remaining_source = self._remaining_source

        if remaining_source.lstrip(" ") and remaining_source.lstrip(" ")[0] == "\n":
            return []

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
            list(itertools.takewhile(lambda s: s == " ", self._remaining_source))
        )
        if space_count == 0:
            return 0

        if space_count % 4 != 0:
            raise UnevenIndentError(self._line, self._column, space_count)
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
            itertools.takewhile(character_predicate, self._remaining_source)
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
            itertools.takewhile(character_predicate, self._remaining_source)
        )

        token = Token(self._line, self._column, resulting_category, characters)

        self._column += len(characters)
        self._source_index += len(characters)

        return token


def _is_identifier_leading_character(c: Text) -> bool:
    return (c.isalpha() and c.isascii()) or c == "_"


def _is_identifier_character(c: Text) -> bool:
    return _is_identifier_leading_character(c) or c.isdigit()
