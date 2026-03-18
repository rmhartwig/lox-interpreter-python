# Lox Interpreter (Python)

This is my implementation of the Lox programming language interpreter from *Crafting Interpreters* by Robert Nystrom.

Everything was written by me following the *Crafting Interpreters* and with help with generative AI.

It’s a full tree-walk interpreter written in Python that can parse and execute Lox programs, including support for functions, closures, classes, and inheritance.

## What it does

The interpreter takes Lox source code and runs it by:

* Tokenizing the input (scanner)
* Parsing it into an AST
* Resolving variable scopes
* Walking the AST to execute the program

## Features

* Variables and block scope
* Expressions (math, comparisons, logic)
* Control flow (`if`, `while`, `for`)
* Functions (including recursion and closures)
* Classes and instances
* Fields and methods
* `this` keyword
* Constructors (`init`)
* Inheritance (`class B < A`)
* Method overriding
* `super` calls

## Project structure

scanner.py        # turns source into tokens
parser.py         # builds the AST
expr.py / stmt.py # AST definitions
resolver.py       # handles variable scope resolution
interpreter.py    # executes the program
environment.py    # manages variable scopes

lox_function.py   # function objects + closures
lox_class.py      # class definitions
lox_instance.py   # class instances
lox.py            # entry point (REPL / file runner)

## Running it

Start the REPL:

bash
```
python lox.py
```

Run a file:

bash
```
python lox.py test.lox
```

## Notes

* This follows the structure of the book pretty closely, just translated into Python
* It’s not optimized — the goal was understanding how interpreters work, not speed
* The resolver was probably the trickiest part (closures + scope tracking)

## Status

Finished Part II (tree-walk interpreter)

## Credit

Assistence:
ChatGPT - OpenAI

Based on:
https://craftinginterpreters.com/
