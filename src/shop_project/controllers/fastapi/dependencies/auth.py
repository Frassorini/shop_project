from typing import Annotated

from dishka import AsyncContainer
from fastapi import Depends, HTTPException

from shop_project.application.authentication.adapters.access_token_verifier import (
    AccessTokenVerifier,
)
from shop_project.application.shared.access_token_payload import AccessTokenPayload
from shop_project.controllers.fastapi.dependencies.di_container import get_container
from shop_project.controllers.fastapi.schemas.oauth2_schema import oauth2_scheme


async def get_access_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
    container: AsyncContainer = Depends(get_container),
) -> AccessTokenPayload:
    verifier = await container.get(AccessTokenVerifier)
    session = verifier.verify_access_token(token)
    if not session:
        raise HTTPException(status_code=401)
    return session
