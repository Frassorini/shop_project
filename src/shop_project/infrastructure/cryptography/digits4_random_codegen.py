from shop_project.infrastructure.cryptography.interfaces.code_generator import (
    CodeGenerator,
)
from shop_project.infrastructure.cryptography.interfaces.entropy_source import (
    EntropySource,
)


class Digits4RandomCodegen(CodeGenerator):
    def __init__(self, entropy_source: EntropySource):
        self._entropy_source = entropy_source
        self._num_digits = 4

    def generate(self) -> str:
        digits = "0123456789"
        random_bytes = self._entropy_source.generate_bytes(self._num_digits)
        return "".join(digits[b % 10] for b in random_bytes)
