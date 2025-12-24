from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import Integer, Numeric, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from shop_project.infrastructure.persistence.database.models.base import Base


class Product(Base):
    __tablename__ = "product"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[int] = mapped_column(Integer(), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)

    def repopulate(
        self, entity_id: UUID, name: str, amount: int, price: Decimal, **kw: Any
    ) -> None:
        self.entity_id = entity_id
        self.name = name
        self.amount = amount
        self.price = price

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)
