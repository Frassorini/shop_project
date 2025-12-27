from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.application.shared.interfaces.interface_session_service import (
    ISessionService,
)


class AccessTokenVerifier:
    def __init__(
        self,
        session_service: ISessionService,
    ) -> None:
        self._session_service: ISessionService = session_service

    def verify_access_token(self, access_token: str) -> AccessTokenPayload | None:
        return self._session_service.verify_access_token(access_token)
