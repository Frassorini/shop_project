from decimal import Decimal
from typing import Self
from uuid import UUID

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.domain.entities.escrow_account import (
    EscrowAccount,
    EscrowAccountState,
)


class EscrowAccountDTO(BaseDTO[EscrowAccount]):
    entity_id: UUID
    state: str
    total_amount: Decimal

    @classmethod
    def to_dto(cls, domain_object: EscrowAccount) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            state=domain_object.state.value,
            total_amount=domain_object.total_amount,
        )

    def to_domain(self) -> EscrowAccount:
        return EscrowAccount.load(
            entity_id=self.entity_id,
            state=EscrowAccountState(self.state),
            total_amount=self.total_amount,
        )
