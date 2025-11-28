from dishka import BaseScope, Component, Provider, Scope, alias, provide
from pydantic import BaseModel, SecretBytes

from shop_project.infrastructure.cryptography.base_64_rand_datagen import (
    Base64RandomDataGenerator,
)
from shop_project.infrastructure.cryptography.bcrypt_hasher import BcryptPasswordHasher
from shop_project.infrastructure.cryptography.interfaces.jwt_signer import JWTSigner
from shop_project.infrastructure.cryptography.interfaces.random_data_generator import (
    RandomDataGenerator,
)
from shop_project.infrastructure.cryptography.interfaces.secret_hasher import (
    SecretHasher,
)
from shop_project.infrastructure.cryptography.pyjwt_signer import PyJWTSigner
from shop_project.infrastructure.env_loader import get_env


class JwtKeyContainer(BaseModel):
    private_key: SecretBytes
    public_key: SecretBytes


class CryptographyProvider(Provider):
    scope = Scope.APP

    def __init__(
        self,
        jwt_keys: JwtKeyContainer,
        *,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ):
        super().__init__(scope, component)

        self.jwt_keys = jwt_keys

    @provide
    def bcrypt_password_hasher(self) -> BcryptPasswordHasher:
        return BcryptPasswordHasher(rounds=int(get_env("BCRYPT_ROUNDS")))

    @provide
    def pyjwt_signer(self) -> PyJWTSigner:
        return PyJWTSigner(
            private_key=self.jwt_keys.private_key.get_secret_value(),
            public_key=self.jwt_keys.public_key.get_secret_value(),
        )

    @provide
    def base64_random_data_generator(self) -> Base64RandomDataGenerator:
        return Base64RandomDataGenerator(
            num_bytes=int(get_env("REFRESH_TOKEN_NUM_BYTES"))
        )

    jwt_signer_proto = alias(PyJWTSigner, provides=JWTSigner)
    secret_hasher_proto = alias(BcryptPasswordHasher, provides=SecretHasher)
    random_data_generator_proto = alias(
        Base64RandomDataGenerator, provides=RandomDataGenerator
    )
