# Represents a single token produced by the scanner.
# Stores type, lexeme, literal value, and line number.
from dataclasses import dataclass
from typing import Any
from token_type import TokenType


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: Any
    line: int

    def __str__(self) -> str:
        return f"{self.type.name} {self.lexeme} {self.literal}"