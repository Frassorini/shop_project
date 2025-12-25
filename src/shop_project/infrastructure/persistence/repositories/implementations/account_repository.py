from shop_project.application.shared.dto.account_dto import AccountDTO
from shop_project.infrastructure.entities.account import Account
from shop_project.infrastructure.persistence.database.models.account import (
    Account as AccountORM,
)
from shop_project.infrastructure.persistence.repositories.base_repository import (
    BaseRepository,
)


class AccountRepository(BaseRepository[AccountORM, AccountDTO, Account]):
    pass
