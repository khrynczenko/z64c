import click

from zx64c.codegen import Environment, Z80CodegenVisitor, SjasmplusSnapshotVisitor
from zx64c.parser import Parser
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
    except ScanError as e:
        print(e.make_error_message())
        return

    parser = Parser(tokens)
    ast = parser.parse()

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
