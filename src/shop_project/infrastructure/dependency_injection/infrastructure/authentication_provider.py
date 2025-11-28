from datetime import timedelta

from dishka import Provider, Scope, provide

from shop_project.infrastructure.authentication.services.secret_service import (
    SecretService,
)
from shop_project.infrastructure.authentication.services.session_service import (
    SessionService,
)
from shop_project.infrastructure.cryptography.interfaces.jwt_signer import JWTSigner
from shop_project.infrastructure.cryptography.interfaces.random_data_generator import (
    RandomDataGenerator,
)
from shop_project.infrastructure.cryptography.interfaces.secret_hasher import (
    SecretHasher,
)
from shop_project.infrastructure.env_loader import get_env


class AuthenticationProvider(Provider):
    scope = Scope.APP

    @provide
    def secret_service(self, secret_hasher: SecretHasher) -> SecretService:
        return SecretService(secret_hasher=secret_hasher)

    @provide
    def session_service(
        self,
        secret_hasher: SecretHasher,
        rand_datagen: RandomDataGenerator,
        data_signer: JWTSigner,
    ) -> SessionService:
        return SessionService(
            secret_hasher=secret_hasher,
            rand_datagen=rand_datagen,
            data_signer=data_signer,
            refresh_ttl=timedelta(seconds=int(get_env("REFRESH_TOKEN_TTL"))),
            access_ttl=timedelta(seconds=int(get_env("ACCESS_TOKEN_TTL"))),
        )
