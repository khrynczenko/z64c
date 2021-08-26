import click

from z64c.codegen import Environment, Z80CodegenVisitor, SjasmplusSnapshotVisitor
from z64c.scanner import Scanner
from z64c.parser import Parser


@click.command()
@click.argument("source", type=str)
def z64c(source: str):
    with open(source, "r") as file:
        source_text = file.read()
    scanner = Scanner(source_text)
    tokens = scanner.scan()
    parser = Parser(tokens)
    ast = parser.parse()
    codegen = Z80CodegenVisitor(Environment())
    sjasmplus_codegen = SjasmplusSnapshotVisitor(codegen, source.rstrip(".z64c"))
    ast.visit(sjasmplus_codegen)


def main():
    z64c()
