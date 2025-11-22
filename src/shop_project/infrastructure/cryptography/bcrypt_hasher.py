import bcrypt

from shop_project.infrastructure.cryptography.interfaces.secret_hasher import (
    SecretHasher,
)
from shop_project.shared.bytes_utils import bytes_to_str, str_to_bytes


class BcryptPasswordHasher(SecretHasher):
    def __init__(self, rounds: int = 12):
        self._rounds = rounds

    def hash(self, password: str) -> str:
        h = bcrypt.hashpw(str_to_bytes(password), bcrypt.gensalt(self._rounds))
        return bytes_to_str(h)

    def verify(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(str_to_bytes(password), str_to_bytes(hashed))
