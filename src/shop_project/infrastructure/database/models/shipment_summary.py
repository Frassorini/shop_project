from typing import Any
from uuid import UUID

from sqlalchemy import (
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shop_project.infrastructure.database.models.base import Base


class ShipmentSummary(Base):
    __tablename__ = "shipment_summary"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    reason: Mapped[str] = mapped_column(String(50), nullable=False)

    items: Mapped[list["ShipmentSummaryItem"]] = relationship(
        back_populates="parent",
        lazy="raise",
        viewonly=True,
    )

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)

    def repopulate(self, entity_id: UUID, reason: str, **kw: Any) -> None:
        self.entity_id = entity_id
        self.reason = reason

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)


class ShipmentSummaryItem(Base):
    __tablename__ = "shipment_summary_item"

    parent_id: Mapped[UUID] = mapped_column(nullable=False)
    product_id: Mapped[UUID] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(Integer(), nullable=False)

    parent: Mapped["ShipmentSummary"] = relationship(
        back_populates="items",
        lazy="raise",
    )

    __table_args__ = (
        PrimaryKeyConstraint("parent_id", "product_id"),
        ForeignKeyConstraint(["parent_id"], ["shipment_summary.entity_id"]),
        ForeignKeyConstraint(["product_id"], ["product.entity_id"]),
    )

    def repopulate(
        self, parent_id: UUID, product_id: UUID, amount: int, **kw: Any
    ) -> None:
        self.parent_id = parent_id
        self.product_id = product_id
        self.amount = amount

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)
