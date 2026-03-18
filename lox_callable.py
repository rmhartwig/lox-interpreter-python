from __future__ import annotations

from abc import ABC, abstractmethod


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int:
        pass

    @abstractmethod
    def call(self, interpreter, arguments):
        pass