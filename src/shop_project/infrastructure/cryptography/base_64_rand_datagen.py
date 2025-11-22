import base64
import secrets

from shop_project.infrastructure.cryptography.interfaces.random_data_generator import (
    RandomDataGenerator,
)


class Base64RandomDataGenerator(RandomDataGenerator):
    def __init__(self, num_bytes: int):
        self._num_bytes = num_bytes

    def generate(self) -> str:
        raw = secrets.token_bytes(self._num_bytes)
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")
