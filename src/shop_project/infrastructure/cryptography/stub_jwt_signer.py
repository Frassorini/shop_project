import json
from datetime import datetime, timedelta, timezone
from typing import Any

from shop_project.infrastructure.cryptography.exceptions import JWTException
from shop_project.infrastructure.cryptography.interfaces.jwt_signer import JWTSigner


class StubJWTSigner(JWTSigner):
    def sign(self, payload: dict[str, Any], ttl: timedelta) -> str:
        """
        Возвращает JSON с полями payload, iat и exp.
        """
        now = datetime.now(tz=timezone.utc)
        payload.setdefault("iat", int(now.timestamp()))
        payload.setdefault("exp", int((now + ttl).timestamp()))
        return json.dumps(payload, separators=(",", ":"))  # минимальный оверхед

    def verify(self, data: str) -> dict[str, Any]:
        """
        Возвращает словарь payload из JSON
        """
        try:
            payload = json.loads(data)
            now_ts = int(datetime.now(tz=timezone.utc).timestamp())
            if "exp" in payload and payload["exp"] < now_ts:
                raise JWTException("Token expired")
            return payload
        except (json.JSONDecodeError, KeyError) as e:
            raise JWTException(f"Invalid token: {e}")
