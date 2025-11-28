from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from shop_project.infrastructure.cryptography.exceptions import JWTException
from shop_project.infrastructure.cryptography.interfaces.jwt_signer import JWTSigner


class PyJWTSigner(JWTSigner):
    def __init__(self, private_key: bytes, public_key: bytes) -> None:
        self._private_key_pem = private_key
        self._public_key_pem = public_key

    def sign(self, payload: dict[str, Any], ttl: timedelta) -> str:
        """
        Подписывает payload, добавляет iat и exp, возвращает JWT строку
        """
        now = datetime.now(tz=timezone.utc)
        payload.setdefault("iat", int(now.timestamp()))
        payload.setdefault("exp", int((now + ttl).timestamp()))

        result = jwt.encode(
            payload=payload, key=self._private_key_pem, algorithm="RS256"
        )

        return result

    def verify(self, data: str) -> dict[str, Any]:
        """
        Проверяет подпись и exp, возвращает словарь payload
        Выбрасывает jwt.ExpiredSignatureError если токен просрочен
        """
        try:
            payload = jwt.decode(data, key=self._public_key_pem, algorithms=["RS256"])
            return payload
        except jwt.PyJWTError:
            raise JWTException
