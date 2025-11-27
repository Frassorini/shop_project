from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import Numeric, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from shop_project.infrastructure.database.models.base import Base


class EscrowAccount(Base):
    __tablename__ = "escrow_account"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)

    def repopulate(
        self, entity_id: UUID, total_amount: Decimal, state: str, **kw: Any
    ) -> None:
        self.entity_id = entity_id
        self.total_amount = total_amount
        self.state = state

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)
