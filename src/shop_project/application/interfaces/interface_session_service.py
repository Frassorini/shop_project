from typing import Protocol

from pydantic import BaseModel, SecretStr

from shop_project.domain.interfaces.subject import Subject
from shop_project.infrastructure.authentication.helpers.access_token_payload import (
    AccessTokenPayload,
)
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.entities.auth_session import (
    AuthSession,
)


class SessionRefresh(BaseModel):
    refresh_token: SecretStr
    access_token: SecretStr


class ISessionService(Protocol):

    def get_refresh_token_fingerprint(self, refresh_token: str) -> str: ...

    def verify_access_token(self, token: str) -> AccessTokenPayload | None: ...

    def create_session(
        self, account: Account, subject: Subject
    ) -> tuple[AuthSession, SessionRefresh]: ...

    def refresh_session(
        self, subject: Subject, session: AuthSession
    ) -> SessionRefresh: ...

    def verify_session(self, session: AuthSession, refresh_token: str) -> bool: ...
