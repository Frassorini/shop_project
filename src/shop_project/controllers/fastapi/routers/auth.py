from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestFormStrict
from pydantic import SecretStr

from shop_project.application.authentication.commands.authentication_service import (
    AuthenticationService,
)
from shop_project.application.authentication.commands.registration_service import (
    RegistrationService,
)
from shop_project.application.authentication.schemas.credential_schema import (
    LoginPasswordCredentialSchema,
)
from shop_project.controllers.fastapi.schemas.oauth2_schema import (
    OAuth2RefreshTokenRequestForm,
    Token,
)

router = APIRouter(route_class=DishkaRoute, prefix="")


@router.post("/refresh")
async def refresh(
    authentication_service: FromDishka[AuthenticationService],
    form_data: Annotated[OAuth2RefreshTokenRequestForm, Depends()],
) -> Token:
    refresh_token = form_data.refresh_token
    session_refresh = await authentication_service.refresh_session_env(refresh_token)
    return Token(
        access_token=session_refresh.access_token.get_secret_value(),
        refresh_token=session_refresh.refresh_token.get_secret_value(),
    )


@router.post("/register")
async def register(
    registration_service: FromDishka[RegistrationService],
    schema: LoginPasswordCredentialSchema,
) -> Token:
    res = await registration_service.register_env(schema)

    return Token(
        access_token=res.access_token.get_secret_value(),
        refresh_token=res.refresh_token.get_secret_value(),
    )


@router.post("/login")
async def login(
    authentication_service: FromDishka[AuthenticationService],
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
) -> Token:
    schema = LoginPasswordCredentialSchema(
        identifier=form_data.username, password_plaintext=SecretStr(form_data.password)
    )
    res = await authentication_service.login_env(schema)

    return Token(
        access_token=res.access_token.get_secret_value(),
        refresh_token=res.refresh_token.get_secret_value(),
    )
