import click

from zx64c.codegen import Environment, Z80CodegenVisitor, SjasmplusSnapshotVisitor
from zx64c.parser import Parser, ParseError
from zx64c.scanner import Scanner, ScanError
from zx64c.typechecker import TypecheckerVisitor, TypecheckError


@click.command()
@click.argument("source", type=str)
def z64c(source: str):
    with open(source, "r") as file:
        source_text = file.read()

    scanner = Scanner(source_text)
    try:
        tokens = scanner.scan()
        for token in tokens:
            print(token)
    except ScanError as e:
        print(e.make_error_message())
        return

    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except ParseError as e:
        print(e.make_error_message())
        return

    typechecker = TypecheckerVisitor()
    try:
        ast.visit(typechecker)
    except TypecheckError as e:
        print(e.make_error_message())
        return

    codegen = Z80CodegenVisitor(Environment())
    sjasmplus_codegen = SjasmplusSnapshotVisitor(codegen, source.rstrip(".zx64c"))
    ast.visit(sjasmplus_codegen)


def main():
    z64c()
