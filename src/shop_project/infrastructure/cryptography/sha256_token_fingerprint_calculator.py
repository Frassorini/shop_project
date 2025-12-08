import hashlib

from shop_project.infrastructure.cryptography.interfaces.token_fingerprint_calculator import (
    TokenFingerprintCalculator,
)
from shop_project.shared.bytes_utils import bytes_to_str, str_to_bytes


class Sha256TokenFingerprintCalculator(TokenFingerprintCalculator):
    """Deterministic fingerprint calculator using SHA-256."""

    def fingerprint(self, token: str) -> str:
        # Преобразуем строку в байты
        token_bytes = str_to_bytes(token)

        # Вычисляем SHA-256
        digest = hashlib.sha256(token_bytes).digest()

        # Возвращаем hex-строку для хранения и поиска
        return bytes_to_str(digest)
