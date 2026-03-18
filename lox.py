import sys
from scanner import Scanner


class Lox:
    had_error = False

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

        for token in tokens:
            print(token)

    @staticmethod
    def error(line: int, message: str):
        Lox.report(line, "", message)

    @staticmethod
    def report(line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        Lox.had_error = True


if __name__ == "__main__":
    Lox.main()