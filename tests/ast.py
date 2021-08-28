"""
Contains modified constructors for all subclasses of the Ast. These constructors
are partially applied with an arbitrary context. They are used in tests that
do not care about node context.
"""

import functools

from z64c.ast import (
    Program,
    Print,
    Assignment,
    Addition,
    Negation,
    Unsignedint,
    Identifier,
    Bool,
)
from z64c.ast import SourceContext

TEST_CONTEXT = SourceContext(0, 0)

# Ast nodes that have already filled context in the constructor
ProgramTC = functools.partial(Program, context=TEST_CONTEXT)
PrintTC = functools.partial(Print, context=TEST_CONTEXT)
AssignmentTC = functools.partial(Assignment, context=TEST_CONTEXT)
AdditionTC = functools.partial(Addition, context=TEST_CONTEXT)
NegationTC = functools.partial(Negation, context=TEST_CONTEXT)
UnsignedintTC = functools.partial(Unsignedint, context=TEST_CONTEXT)
IdentifierTC = functools.partial(Identifier, context=TEST_CONTEXT)
BoolTC = functools.partial(Bool, context=TEST_CONTEXT)
