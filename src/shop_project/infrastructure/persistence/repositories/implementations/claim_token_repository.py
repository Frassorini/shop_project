from shop_project.application.shared.dto.claim_token_dto import ClaimTokenDTO
from shop_project.infrastructure.entities.claim_token import ClaimToken
from shop_project.infrastructure.persistence.database.models.claim_token import (
    ClaimToken as ClaimTokenORM,
)
from shop_project.infrastructure.persistence.repositories.base_repository import (
    BaseRepository,
)


class ClaimTokenRepository(BaseRepository[ClaimTokenORM, ClaimTokenDTO, ClaimToken]):
    pass
