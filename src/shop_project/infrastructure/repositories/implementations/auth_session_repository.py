from shop_project.application.dto.auth_session_dto import AuthSessionDTO
from shop_project.infrastructure.database.models.auth_session import (
    AuthSession as AuthSessionORM,
)
from shop_project.infrastructure.entities.auth_session import AuthSession
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class AuthSessionRepository(
    BaseRepository[AuthSessionORM, AuthSessionDTO, AuthSession]
):
    pass
