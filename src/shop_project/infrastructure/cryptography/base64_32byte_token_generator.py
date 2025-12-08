import base64
import secrets

from shop_project.infrastructure.cryptography.interfaces.entropy_source import (
    EntropySource,
)
from shop_project.infrastructure.cryptography.interfaces.token_generator import (
    TokenGenerator,
)


class Base64_32ByteTokenGenerator(TokenGenerator):
    def __init__(self, entropy_source: EntropySource):
        self._entropy_source = entropy_source
        self._num_bytes = 32

    def generate(self) -> str:
        raw = secrets.token_bytes(self._num_bytes)
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")
