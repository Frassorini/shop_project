from shop_project.infrastructure.cryptography.interfaces.password_hasher import (
    PasswordHasher,
)


class StubHasher(PasswordHasher):
    def __init__(self):
        pass

    def hash(self, password: str) -> str:
        return password

    def verify(self, password: str, hashed: str) -> bool:
        if password == hashed:
            return True
        return False
