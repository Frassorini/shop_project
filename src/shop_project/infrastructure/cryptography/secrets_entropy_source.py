import secrets

from shop_project.infrastructure.cryptography.interfaces.entropy_source import (
    EntropySource,
)


class SecretsEntropySource(EntropySource):
    def generate_bytes(self, num_bytes: int) -> bytes:
        return secrets.token_bytes(num_bytes)
