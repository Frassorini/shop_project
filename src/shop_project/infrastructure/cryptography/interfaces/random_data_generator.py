from typing import Protocol


class RandomDataGenerator(Protocol):
    def generate(self) -> str:
        """Возвращает криптографически безопасную случайную строку фиксированной длины."""
        ...
