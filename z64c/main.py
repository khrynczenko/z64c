import click

from z64c.ast import Environment
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
    ast.emit(Environment())


def main():
    z64c()
