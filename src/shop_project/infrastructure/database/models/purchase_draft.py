from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shop_project.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from shop_project.infrastructure.database.models.customer import Customer


class PurchaseDraft(Base):
    __tablename__ = "purchase_draft"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    customer_id: Mapped[UUID] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)

    items: Mapped[list["PurchaseDraftItem"]] = relationship(
        back_populates="parent",
        lazy="raise",
        viewonly=True,
    )

    customer: Mapped["Customer"] = relationship(
        lazy="raise",
    )

    __table_args__ = (
        PrimaryKeyConstraint("entity_id"),
        ForeignKeyConstraint(["customer_id"], ["customer.entity_id"]),
    )

    def repopulate(
        self, entity_id: UUID, customer_id: UUID, state: str, **kw: Any
    ) -> None:
        self.entity_id = entity_id
        self.customer_id = customer_id
        self.state = state

    def __init__(self, **kw: Any):
        super().__init__()
        self.repopulate(**kw)


class PurchaseDraftItem(Base):
    __tablename__ = "purchase_draft_item"

    parent_id: Mapped[UUID] = mapped_column(nullable=False)
    product_id: Mapped[UUID] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(Integer(), nullable=False)

    parent: Mapped["PurchaseDraft"] = relationship(
        back_populates="items",
        lazy="raise",
    )

    __table_args__ = (
        PrimaryKeyConstraint("parent_id", "product_id"),
        ForeignKeyConstraint(
            ["parent_id"],
            ["purchase_draft.entity_id"],
        ),
        ForeignKeyConstraint(["product_id"], ["product.entity_id"]),
    )

    def repopulate(
        self, parent_id: UUID, product_id: UUID, amount: int, **kw: Any
    ) -> None:
        self.parent_id = parent_id
        self.product_id = product_id
        self.amount = amount

    def __init__(self, **kw: Any):
        super().__init__()
        self.repopulate(**kw)
