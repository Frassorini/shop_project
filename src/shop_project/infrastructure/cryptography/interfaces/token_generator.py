from typing import Protocol


class TokenGenerator(Protocol):
    def generate(self) -> str:
        """Возвращает криптографически безопасную случайную строку фиксированной длины."""
        ...
