from shop_project.application.dto.escrow_account_dto import EscrowAccountDTO
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.infrastructure.database.models.escrow_account import (
    EscrowAccount as EscrowAccountORM,
)
from shop_project.infrastructure.repositories.base_repository import BaseRepository


class EscrowAccountRepository(
    BaseRepository[EscrowAccountORM, EscrowAccountDTO, EscrowAccount]
):
    pass
