from typing import Protocol


class CodeGenerator(Protocol):
    def generate(self) -> str: ...
