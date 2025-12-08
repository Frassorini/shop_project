from datetime import timedelta

from dishka import Provider, Scope, alias, provide

from shop_project.application.interfaces.interface_account_service import (
    IAccountService,
)
from shop_project.application.interfaces.interface_notification import (
    EmailNotificationService,
    SMSNotificationService,
)
from shop_project.application.interfaces.interface_totp_service import ITotpService
from shop_project.infrastructure.authentication.services.account_service import (
    AccountService,
)
from shop_project.infrastructure.authentication.services.session_service import (
    SessionService,
)
from shop_project.infrastructure.authentication.services.totp_service import TotpService
from shop_project.infrastructure.cryptography.interfaces.code_generator import (
    CodeGenerator,
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
from shop_project.infrastructure.env_loader import get_env


class AuthenticationProvider(Provider):
    scope = Scope.APP

    @provide
    def account_service(self, password_hasher: PasswordHasher) -> AccountService:
        return AccountService(password_hasher=password_hasher)

    @provide
    def session_service(
        self,
        token_fingerprint_calculator: TokenFingerprintCalculator,
        rand_datagen: TokenGenerator,
        data_signer: JWTSigner,
    ) -> SessionService:
        return SessionService(
            token_fingerprint_calculator=token_fingerprint_calculator,
            rand_datagen=rand_datagen,
            data_signer=data_signer,
            refresh_ttl=timedelta(seconds=int(get_env("REFRESH_TOKEN_TTL"))),
            access_ttl=timedelta(seconds=int(get_env("ACCESS_TOKEN_TTL"))),
        )

    @provide
    def totp_service(
        self,
        password_hasher: PasswordHasher,
        code_generator: CodeGenerator,
        email_notification_service: EmailNotificationService,
        sms_notification_service: SMSNotificationService,
    ) -> TotpService:
        return TotpService(
            password_hasher=password_hasher,
            code_generator=code_generator,
            email_notfication_service=email_notification_service,
            sms_notfication_service=sms_notification_service,
            totp_ttl=timedelta(seconds=int(get_env("TOTP_TTL"))),
            email_sender=get_env("TOTP_EMAIL_SENDER"),
            sms_sender=get_env("TOTP_SMS_SENDER"),
        )

    account_service_proto = alias(AccountService, provides=IAccountService)
    totp_service_proto = alias(TotpService, provides=ITotpService)
