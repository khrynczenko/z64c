from __future__ import annotations


class Type:
    def __init__(self, name: str):
        self._name = name

    def __eq__(self, rhs: Type):
        return self._name == rhs._name

    def __str__(self):
        return self._name


VOID = Type("void")
U8 = Type("u8")
BOOL = Type("bool")
