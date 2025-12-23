from shop_project.application.dto.claim_token_dto import ClaimTokenDTO
from shop_project.infrastructure.database.models.claim_token import (
    ClaimToken as ClaimTokenORM,
)
from shop_project.infrastructure.entities.claim_token import ClaimToken
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class ClaimTokenRepository(BaseRepository[ClaimTokenORM, ClaimTokenDTO, ClaimToken]):
    pass
