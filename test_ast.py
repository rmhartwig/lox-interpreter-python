# Simple test file for building and printing ASTs.
# Helps verify parsing and AST structure.
from ast_printer import AstPrinter
from expr import Binary, Grouping, Literal, Unary
from lox_token import Token
from token_type import TokenType


expression = Binary(
    Unary(
        Token(TokenType.MINUS, "-", None, 1),
        Literal(123),
    ),
    Token(TokenType.STAR, "*", None, 1),
    Grouping(
        Literal(45.67)
    ),
)

print(AstPrinter().print(expression))