from shop_project.application.entities.auth_session import AuthSession
from shop_project.application.shared.dto.auth_session_dto import AuthSessionDTO
from shop_project.infrastructure.persistence.database.models.auth_session import (
    AuthSession as AuthSessionORM,
)
from shop_project.infrastructure.persistence.repositories.base_repository import (
    BaseRepository,
)


class AuthSessionRepository(
    BaseRepository[AuthSessionORM, AuthSessionDTO, AuthSession]
):
    pass
