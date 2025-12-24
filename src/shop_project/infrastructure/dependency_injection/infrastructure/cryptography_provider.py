from dishka import BaseScope, Component, Provider, Scope, alias, provide
from pydantic import BaseModel, SecretBytes

from shop_project.infrastructure.cryptography.base64_32byte_token_generator import (
    Base64_32ByteTokenGenerator,
)
from shop_project.infrastructure.cryptography.bcrypt_hasher import BcryptPasswordHasher
from shop_project.infrastructure.cryptography.digits4_random_codegen import (
    Digits4RandomCodegen,
)
from shop_project.infrastructure.cryptography.interfaces.code_generator import (
    CodeGenerator,
)
from shop_project.infrastructure.cryptography.interfaces.entropy_source import (
    EntropySource,
)
from shop_project.infrastructure.cryptography.interfaces.jwt_signer import JWTSigner
from shop_project.infrastructure.cryptography.interfaces.password_hasher import (
    PasswordHasher,
)
from shop_project.infrastructure.cryptography.interfaces.token_fingerprint_calculator import (
    TokenFingerprintCalculator,
)
from shop_project.infrastructure.cryptography.interfaces.token_generator import (
    TokenGenerator,
)
from shop_project.infrastructure.cryptography.pyjwt_signer import PyJWTSigner
from shop_project.infrastructure.cryptography.secrets_entropy_source import (
    SecretsEntropySource,
)
from shop_project.infrastructure.cryptography.sha256_token_fingerprint_calculator import (
    Sha256TokenFingerprintCalculator,
)
from shop_project.infrastructure.cryptography.stub_hasher import StubHasher
from shop_project.infrastructure.cryptography.stub_jwt_signer import StubJWTSigner
from shop_project.infrastructure.env_loader import get_env


class JwtKeyContainer(BaseModel):
    private_key: SecretBytes
    public_key: SecretBytes


class CryptographyProvider(Provider):
    scope = Scope.APP

    def __init__(
        self,
        jwt_keys: JwtKeyContainer,
        use_stubs: bool = False,
        *,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ):
        super().__init__(scope, component)
        self.jwt_keys = jwt_keys

    @provide
    def entropy_source(self) -> SecretsEntropySource:
        return SecretsEntropySource()

    @provide
    def sha256_token_fingerprint_calculator(self) -> Sha256TokenFingerprintCalculator:
        return Sha256TokenFingerprintCalculator()

    @provide
    def bcrypt_password_hasher(self) -> BcryptPasswordHasher:
        return BcryptPasswordHasher(rounds=int(get_env("BCRYPT_ROUNDS")))

    @provide
    def stub_password_hasher(self) -> StubHasher:
        return StubHasher()

    @provide
    def password_hasher_proto(self) -> PasswordHasher:
        if get_env("CRYPTO_USE_STUBS") == "true":
            return self.stub_password_hasher()
        return self.bcrypt_password_hasher()

    @provide
    def stub_jwt_signer(self) -> StubJWTSigner:
        return StubJWTSigner()

    @provide
    def pyjwt_signer(self) -> PyJWTSigner:
        return PyJWTSigner(
            private_key=self.jwt_keys.private_key.get_secret_value(),
            public_key=self.jwt_keys.public_key.get_secret_value(),
        )

    @provide
    def jwt_signer_proto(self) -> JWTSigner:
        if get_env("CRYPTO_USE_STUBS") == "true":
            return self.stub_jwt_signer()
        return self.pyjwt_signer()

    @provide
    def base64_32byte_token_generator(
        self, entropy_source: EntropySource
    ) -> Base64_32ByteTokenGenerator:
        return Base64_32ByteTokenGenerator(entropy_source=entropy_source)

    @provide
    def digits4_random_codegen(
        self, entropy_source: EntropySource
    ) -> Digits4RandomCodegen:
        return Digits4RandomCodegen(entropy_source=entropy_source)

    entropy_source_proto = alias(SecretsEntropySource, provides=EntropySource)
    token_fingerprint_calculator_proto = alias(
        Sha256TokenFingerprintCalculator, provides=TokenFingerprintCalculator
    )
    random_data_generator_proto = alias(
        Base64_32ByteTokenGenerator, provides=TokenGenerator
    )
    digits4_random_codegen_proto = alias(Digits4RandomCodegen, provides=CodeGenerator)
