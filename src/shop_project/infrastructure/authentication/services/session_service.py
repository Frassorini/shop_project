from datetime import datetime, timedelta, timezone
from uuid import uuid4

from plum import dispatch, overload
from pydantic import SecretStr

from shop_project.application.shared.interfaces.interface_session_service import (
    ISessionService,
    SessionRefresh,
)
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.domain.interfaces.subject import Subject, SubjectEnum
from shop_project.infrastructure.authentication.exceptions import (
    AuthSessionExpiredException,
    PermissionException,
)
from shop_project.infrastructure.authentication.helpers.access_token_payload import (
    AccessTokenPayload,
)
from shop_project.infrastructure.cryptography.exceptions import JWTException
from shop_project.infrastructure.cryptography.interfaces.jwt_signer import JWTSigner
from shop_project.infrastructure.cryptography.interfaces.token_fingerprint_calculator import (
    TokenFingerprintCalculator,
)
from shop_project.infrastructure.cryptography.interfaces.token_generator import (
    TokenGenerator,
)
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.entities.auth_session import (
    AuthSession,
)


class SessionService(ISessionService):
    def __init__(
        self,
        token_fingerprint_calculator: TokenFingerprintCalculator,
        rand_datagen: TokenGenerator,
        data_signer: JWTSigner,
        refresh_ttl: timedelta,
        access_ttl: timedelta,
    ) -> None:
        self.token_fingerprint_calculator = token_fingerprint_calculator
        self.rand_datagen = rand_datagen
        self.data_signer = data_signer
        self.refresh_ttl = refresh_ttl
        self.access_ttl = access_ttl

    def get_refresh_token_fingerprint(self, refresh_token: str) -> str:
        return self.token_fingerprint_calculator.fingerprint(refresh_token)

    def verify_access_token(self, token: str) -> AccessTokenPayload | None:
        try:
            self.data_signer.verify(token)
        except JWTException:
            return None
        return AccessTokenPayload.model_validate(self.data_signer.verify(token))

    def create_session(
        self, account: Account, subject: Subject
    ) -> tuple[AuthSession, SessionRefresh]:
        refresh_token = self.rand_datagen.generate()
        access_token = self.data_signer.sign(
            self._create_access_token_payload(subject).model_dump(mode="json"),
            self.access_ttl,
        )

        session = AuthSession(
            entity_id=uuid4(),
            account_id=account.entity_id,
            refresh_token_fingerprint=self.token_fingerprint_calculator.fingerprint(
                refresh_token
            ),
            issued_at=datetime.now(tz=timezone.utc),
            expiration=datetime.now(tz=timezone.utc) + self.refresh_ttl,
        )

        return session, SessionRefresh(
            refresh_token=SecretStr(refresh_token),
            access_token=SecretStr(access_token),
        )

    def refresh_session(self, subject: Subject, session: AuthSession) -> SessionRefresh:
        if subject.entity_id != session.account_id:
            raise PermissionException
        if session.expiration < datetime.now(tz=timezone.utc):
            raise AuthSessionExpiredException

        new_refresh_token = self.rand_datagen.generate()
        access_token = self.data_signer.sign(
            self._create_access_token_payload(subject).model_dump(mode="json"),
            self.access_ttl,
        )

        session.update_refresh_token_fingerprint(
            self.get_refresh_token_fingerprint(new_refresh_token)
        )
        session.expiration = datetime.now(tz=timezone.utc) + self.refresh_ttl

        return SessionRefresh(
            refresh_token=SecretStr(new_refresh_token),
            access_token=SecretStr(access_token),
        )

    def verify_session(self, session: AuthSession, refresh_token: str) -> bool:
        if (
            session.refresh_token_fingerprint
            == self.token_fingerprint_calculator.fingerprint(refresh_token)
        ):
            return True
        return False

    @overload
    def _create_access_token_payload(self, subject: Customer) -> AccessTokenPayload:
        return AccessTokenPayload(
            subject_type=SubjectEnum.CUSTOMER, account_id=subject.entity_id
        )

    @overload
    def _create_access_token_payload(self, subject: Employee) -> AccessTokenPayload:
        return AccessTokenPayload(
            subject_type=SubjectEnum.EMPLOYEE, account_id=subject.entity_id
        )

    @overload
    def _create_access_token_payload(self, subject: Manager) -> AccessTokenPayload:
        return AccessTokenPayload(
            subject_type=SubjectEnum.MANAGER, account_id=subject.entity_id
        )

    @overload
    def _create_access_token_payload(self, subject: Subject) -> AccessTokenPayload:
        raise NotImplementedError

    @dispatch
    def _create_access_token_payload(self, subject: Subject) -> AccessTokenPayload: ...
