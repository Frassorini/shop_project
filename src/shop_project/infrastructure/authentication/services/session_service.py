from datetime import datetime, timedelta, timezone
from uuid import uuid4

from plum import dispatch, overload
from pydantic import BaseModel

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.infrastructure.authentication.exceptions import (
    AuthSessionExpiredException,
    PermissionException,
)
from shop_project.infrastructure.authentication.helpers.access_token_payload import (
    AccessTokenPayload,
)
from shop_project.infrastructure.authentication.helpers.subject_type_union import (
    SubjectTypeUnion,
)
from shop_project.infrastructure.cryptography.exceptions import JWTException
from shop_project.infrastructure.cryptography.interfaces.jwt_signer import JWTSigner
from shop_project.infrastructure.cryptography.interfaces.random_data_generator import (
    RandomDataGenerator,
)
from shop_project.infrastructure.cryptography.interfaces.secret_hasher import (
    SecretHasher,
)
from shop_project.infrastructure.entities.account import Account, SubjectType
from shop_project.infrastructure.entities.auth_session import (
    AuthSession,
)


class SessionRefresh(BaseModel):
    refresh_token: str
    access_token: str


class SessionService:
    def __init__(
        self,
        secret_hasher: SecretHasher,
        rand_datagen: RandomDataGenerator,
        data_signer: JWTSigner,
        refresh_ttl: timedelta,
        access_ttl: timedelta,
    ) -> None:
        self.secret_hasher = secret_hasher
        self.rand_datagen = rand_datagen
        self.data_signer = data_signer
        self.refresh_ttl = refresh_ttl
        self.access_ttl = access_ttl

    def verify_access_token(self, token: str) -> AccessTokenPayload | None:
        try:
            self.data_signer.verify(token)
        except JWTException:
            return None
        return AccessTokenPayload.model_validate(self.data_signer.verify(token))

    def create_session(
        self, account: Account, subject: SubjectTypeUnion
    ) -> tuple[AuthSession, SessionRefresh]:
        refresh_token = self.rand_datagen.generate()
        access_token = self.data_signer.sign(
            self._create_access_token_payload(subject).model_dump(mode="json"),
            self.access_ttl,
        )

        session = AuthSession(
            entity_id=uuid4(),
            account_id=account.entity_id,
            refresh_token=refresh_token,
            issued_at=datetime.now(tz=timezone.utc),
            expires_at=datetime.now(tz=timezone.utc) + self.refresh_ttl,
        )

        return session, SessionRefresh(
            refresh_token=refresh_token,
            access_token=access_token,
        )

    def refresh_session(
        self, subject: SubjectTypeUnion, session: AuthSession, refresh_token: str
    ) -> SessionRefresh:
        if subject.entity_id != session.account_id:
            raise PermissionException
        if not self.verify_session(session, refresh_token):
            raise PermissionException
        if session.expires_at < datetime.now(tz=timezone.utc):
            raise AuthSessionExpiredException

        refresh_token = self.rand_datagen.generate()
        access_token = self.data_signer.sign(
            self._create_access_token_payload(subject).model_dump(mode="json"),
            self.access_ttl,
        )

        session.update_refresh_token_hash(self.rand_datagen.generate())

        return SessionRefresh(
            refresh_token=refresh_token,
            access_token=access_token,
        )

    def verify_session(self, session: AuthSession, refresh_token: str) -> bool:
        if session.refresh_token == refresh_token:
            return True
        return False

    @overload
    def _create_access_token_payload(self, subject: Customer) -> AccessTokenPayload:
        return AccessTokenPayload(
            subject_type=SubjectType.CUSTOMER, account_id=subject.entity_id
        )

    @overload
    def _create_access_token_payload(self, subject: Employee) -> AccessTokenPayload:
        return AccessTokenPayload(
            subject_type=SubjectType.EMPLOYEE, account_id=subject.entity_id
        )

    @overload
    def _create_access_token_payload(self, subject: Manager) -> AccessTokenPayload:
        return AccessTokenPayload(
            subject_type=SubjectType.MANAGER, account_id=subject.entity_id
        )

    @overload
    def _create_access_token_payload(
        self, subject: SubjectTypeUnion
    ) -> AccessTokenPayload:
        raise NotImplementedError

    @dispatch
    def _create_access_token_payload(
        self, subject: SubjectTypeUnion
    ) -> AccessTokenPayload: ...
