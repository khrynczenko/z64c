# zx64c

## What is `zx64` and `zx64c`

`zx64` is a small language designed with a couple things in mind, having python
like syntax and C like semantics, and targeting retro machines.
`zx64c` is a compiler for this language and in the meantime forms the
specification of the language.

## The state of `zx64c`

This is a hobby project meant for learning language and compiler design
together with some retro machine architecture. The only available target
for the compiler is **Z80** assembly in text format (specifically for the
[**sjasmplus**](https://github.com/z00m128/sjasmplus)).

### Implemented features

All the fundamental compilation steps are implemented, i.e.:

- scanning,
- parsing,
- typechecking,
- code generation,

but as of now no code optimization is implemented.

As for the language, the following are implemented:

- 8-bit unsigned and signed integer types,
- bool type,
- variable definitions,
- lexical scope for functions and other blocks,
- function definitions and recursion,
- `if` statement,
- addition, subtraction, negation and comparison operators.

## How to use

```sh
zx64c source.zx64 > source.zx80
sjasmplus source.zx80
```

Then you can run the snapshot produced by `sjasmplus` in some emulator
like [zesarux](https://github.com/chernandezba/zesarux).

## zx64 example

```python
def print_digit(digit: u8) -> void:
    let ascii_shift: u8 = 48
    print(digit + ascii_shift)

def main() -> void:
    let digit: u8 = 1
    print_digit(digit)
```
