from typing import Type

from dishka import Provider, Scope, provide

from shop_project.application.authentication.adapters.access_token_verifier import (
    AccessTokenVerifier,
)
from shop_project.application.authentication.commands.account_service import (
    AccountService,
)
from shop_project.application.authentication.commands.authentication_service import (
    AuthenticationService,
)
from shop_project.application.authentication.commands.registration_service import (
    RegistrationService,
)
from shop_project.application.authentication.commands.totp_challenge_service import (
    TotpChallengeService,
)
from shop_project.application.shared.interfaces.interface_account_service import (
    IAccountService,
)
from shop_project.application.shared.interfaces.interface_query_builder import (
    IQueryBuilder,
)
from shop_project.application.shared.interfaces.interface_session_service import (
    ISessionService,
)
from shop_project.application.shared.interfaces.interface_totp_service import (
    ITotpService,
)
from shop_project.application.shared.interfaces.interface_unit_of_work import (
    IUnitOfWorkFactory,
)


class AuthApplicationProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def register_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        account_service: IAccountService,
        totp_service: ITotpService,
        session_service: ISessionService,
    ) -> RegistrationService:
        return RegistrationService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            account_service=account_service,
            totp_service=totp_service,
            session_service=session_service,
        )

    @provide
    async def authentication_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        account_service: IAccountService,
        totp_service: ITotpService,
        session_service: ISessionService,
    ) -> AuthenticationService:
        return AuthenticationService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            account_service=account_service,
            totp_service=totp_service,
            session_service=session_service,
        )

    @provide
    async def totp_challenge_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        totp_service: ITotpService,
    ) -> TotpChallengeService:
        return TotpChallengeService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            totp_service=totp_service,
        )

    @provide
    async def account_service(
        self,
        unit_of_work_factory: IUnitOfWorkFactory,
        query_builder_type: Type[IQueryBuilder],
        account_service: IAccountService,
        totp_service: ITotpService,
        session_service: ISessionService,
    ) -> AccountService:
        return AccountService(
            unit_of_work_factory=unit_of_work_factory,
            query_builder_type=query_builder_type,
            account_service=account_service,
            totp_service=totp_service,
            session_service=session_service,
        )

    @provide
    async def access_token_verifier(
        self,
        session_service: ISessionService,
    ) -> AccessTokenVerifier:
        return AccessTokenVerifier(
            session_service=session_service,
        )
