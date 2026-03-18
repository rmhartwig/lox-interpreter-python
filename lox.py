# Entry point for the interpreter.
# Handles running files or starting the REPL,
# and coordinates scanning → parsing → resolving → interpreting.
import sys
sys.modules["lox"] = sys.modules[__name__]

from scanner import Scanner
from parser import Parser
from interpreter import Interpreter
from resolver import Resolver
from token_type import TokenType


class Lox:
    interpreter = Interpreter()

    had_error = False
    had_runtime_error = False

    @staticmethod
    def main():
        args = sys.argv[1:]

        if len(args) > 1:
            print("Usage: pylox [script]")
            sys.exit(64)
        elif len(args) == 1:
            Lox.run_file(args[0])
        else:
            Lox.run_prompt()

    @staticmethod
    def run_file(path: str):
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        Lox.run(source)

        if Lox.had_error:
            sys.exit(65)

        if Lox.had_runtime_error:
            sys.exit(70)

    @staticmethod
    def run_prompt():
        while True:
            try:
                line = input("> ")
                Lox.run(line)
                Lox.had_error = False
            except EOFError:
                break

    @staticmethod
    def run(source: str):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        parser = Parser(tokens)
        statements = parser.parse()

        if Lox.had_error:
            return

        resolver = Resolver(Lox.interpreter)
        resolver.resolve(statements)

        if Lox.had_error:
            return

        Lox.interpreter.interpret(statements)

    @staticmethod
    def error(line: int, message: str):
        Lox.report(line, "", message)

    @staticmethod
    def token_error(token, message: str):
        if token.type == TokenType.EOF:
            Lox.report(token.line, " at end", message)
        else:
            Lox.report(token.line, f" at '{token.lexeme}'", message)

    @staticmethod
    def runtime_error(error):
        print(f"{error}\n[line {error.token.line}]", file=sys.stderr)
        Lox.had_runtime_error = True

    @staticmethod
    def report(line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        Lox.had_error = True


if __name__ == "__main__":
    Lox.main()