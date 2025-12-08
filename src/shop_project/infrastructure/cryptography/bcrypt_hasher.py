import bcrypt

from shop_project.infrastructure.cryptography.interfaces.password_hasher import (
    PasswordHasher,
)
from shop_project.shared.bytes_utils import bytes_to_str, str_to_bytes


class BcryptPasswordHasher(PasswordHasher):
    def __init__(self, rounds: int):
        self._rounds = rounds

    def hash(self, password: str) -> str:
        h = bcrypt.hashpw(str_to_bytes(password), bcrypt.gensalt(self._rounds))
        return bytes_to_str(h)

    def verify(self, password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(str_to_bytes(password), str_to_bytes(hashed))
        except ValueError:
            return False
