from datetime import datetime, timedelta, timezone

from plum import dispatch, overload

from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.manager import Manager
from shop_project.infrastructure.authentication.entities.auth_session import (
    AuthSession,
    CustomerSession,
    EmployeeSession,
    ManagerSession,
)
from shop_project.infrastructure.authentication.exceptions import (
    AuthSessionExpiredException,
)
from shop_project.infrastructure.authentication.helpers.access_token_payload import (
    AccessTokenPayload,
    SessionType,
)
from shop_project.infrastructure.authentication.helpers.subject import Subject
from shop_project.infrastructure.cryptography.interfaces.jwt_signer import JWTSigner
from shop_project.infrastructure.cryptography.interfaces.random_data_generator import (
    RandomDataGenerator,
)


class SessionService:
    def __init__(
        self,
        rand_datagen: RandomDataGenerator,
        data_signer: JWTSigner,
        refresh_ttl: timedelta,
        access_ttl: timedelta,
    ) -> None:
        self.rand_datagen = rand_datagen
        self.data_signer = data_signer
        self.refresh_ttl = refresh_ttl
        self.access_ttl = access_ttl

    def verify_access_token(self, token: str) -> AccessTokenPayload:
        return AccessTokenPayload.from_dict(self.data_signer.verify(token))

    @overload
    def create_session(self, subject: Customer) -> AuthSession:
        return CustomerSession(
            subject_id=subject.entity_id,
            ttl=self.refresh_ttl,
            refresh_token=self.rand_datagen.generate(),
        )

    @overload
    def create_session(self, subject: Employee) -> AuthSession:
        return EmployeeSession(
            subject_id=subject.entity_id,
            ttl=self.refresh_ttl,
            refresh_token=self.rand_datagen.generate(),
        )

    @overload
    def create_session(self, subject: Manager) -> AuthSession:
        return ManagerSession(
            subject_id=subject.entity_id,
            ttl=self.refresh_ttl,
            refresh_token=self.rand_datagen.generate(),
        )

    @dispatch
    def create_session(self, subject: Subject) -> AuthSession: ...

    def create_access_token(self, subject: Subject, session: AuthSession) -> str:
        time_now = datetime.now(tz=timezone.utc)

        if session.expires_at < time_now:
            raise AuthSessionExpiredException

        session.update_refresh_token(self.rand_datagen.generate())

        return self.data_signer.sign(
            self._create_access_token_payload(subject).to_dict()
        )

    @overload
    def _create_access_token_payload(self, subject: Customer) -> AccessTokenPayload:
        return AccessTokenPayload(
            session_type=SessionType.CUSTOMER, subject_id=subject.entity_id
        )

    @overload
    def _create_access_token_payload(self, subject: Employee) -> AccessTokenPayload:
        return AccessTokenPayload(
            session_type=SessionType.EMPLOYEE, subject_id=subject.entity_id
        )

    @overload
    def _create_access_token_payload(self, subject: Manager) -> AccessTokenPayload:
        return AccessTokenPayload(
            session_type=SessionType.MANAGER, subject_id=subject.entity_id
        )

    @overload
    def _create_access_token_payload(self, subject: Subject) -> AccessTokenPayload:
        raise NotImplementedError

    @dispatch
    def _create_access_token_payload(self, subject: Subject) -> AccessTokenPayload: ...
