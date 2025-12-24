from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shop_project.infrastructure.persistence.database.models.base import Base
from shop_project.infrastructure.persistence.database.utc_datetime import UTCDateTime

if TYPE_CHECKING:
    from shop_project.infrastructure.persistence.database.models.customer import (
        Customer,
    )
    from shop_project.infrastructure.persistence.database.models.escrow_account import (
        EscrowAccount,
    )


class PurchaseActive(Base):
    __tablename__ = "purchase_active"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    customer_id: Mapped[UUID] = mapped_column(nullable=False)
    escrow_account_id: Mapped[UUID] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    reserved_until: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False
    )

    items: Mapped[list["PurchaseActiveItem"]] = relationship(
        back_populates="parent",
        lazy="raise",
        viewonly=True,
    )

    escrow_account: Mapped["EscrowAccount"] = relationship(
        lazy="raise",
    )

    customer: Mapped["Customer"] = relationship(
        lazy="raise",
    )

    __table_args__ = (
        PrimaryKeyConstraint("entity_id"),
        ForeignKeyConstraint(["escrow_account_id"], ["escrow_account.entity_id"]),
        ForeignKeyConstraint(["customer_id"], ["customer.entity_id"]),
    )

    def repopulate(
        self,
        entity_id: UUID,
        customer_id: UUID,
        escrow_account_id: UUID,
        state: str,
        reserved_until: datetime,
        **kw: Any,
    ) -> None:
        self.entity_id = entity_id
        self.customer_id = customer_id
        self.escrow_account_id = escrow_account_id
        self.state = state
        self.reserved_until = reserved_until

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)


class PurchaseActiveItem(Base):
    __tablename__ = "purchase_active_item"

    parent_id: Mapped[UUID] = mapped_column(nullable=False)
    product_id: Mapped[UUID] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(Integer(), nullable=False)

    parent: Mapped["PurchaseActive"] = relationship(
        back_populates="items",
        lazy="raise",
    )

    __table_args__ = (
        PrimaryKeyConstraint("parent_id", "product_id"),
        ForeignKeyConstraint(["parent_id"], ["purchase_active.entity_id"]),
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
