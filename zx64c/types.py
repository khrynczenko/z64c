import enum

from enum import Enum


@enum.unique
class Type(Enum):
    VOID = enum.auto()
    U8 = enum.auto()
    BOOL = enum.auto()
