from shop_project.application.dto.external_id_totp_dto import ExternalIdTotpDTO
from shop_project.infrastructure.entities.external_id_totp import ExternalIdTotp
from shop_project.infrastructure.persistence.database.models.external_id_totp import (
    ExternalIdTotp as ExternalIdTotpORM,
)
from shop_project.infrastructure.persistence.repositories.base_repository import (
    BaseRepository,
)


class ExternalIdTotpRepository(
    BaseRepository[ExternalIdTotpORM, ExternalIdTotpDTO, ExternalIdTotp]
):
    pass
