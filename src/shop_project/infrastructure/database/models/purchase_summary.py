from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import Mapped, relationship

from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.models.escrow_account import EscrowAccount
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class PurchaseSummary(Base):
    __tablename__ = "purchase_summary"

    entity_id = Column(UUIDBinary(), nullable=False)
    customer_id = Column(UUIDBinary(), nullable=False)
    escrow_account_id = Column(UUIDBinary(), nullable=False)
    reason = Column(String(50), nullable=False)

    items: Mapped[list["PurchaseSummaryItem"]] = relationship(
        back_populates="purchase_summary",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    escrow_account: Mapped["EscrowAccount"] = relationship(
        lazy="raise",
    )

    __table_args__ = (
        PrimaryKeyConstraint("entity_id"),
        ForeignKeyConstraint(["escrow_account_id"], ["escrow_account.entity_id"]),
    )


class PurchaseSummaryItem(Base):
    __tablename__ = "purchase_summary_item"

    purchase_summary_id = Column(UUIDBinary(), nullable=False)
    product_id = Column(UUIDBinary(), nullable=False)
    amount = Column(Integer(), nullable=False)

    purchase_summary: Mapped["PurchaseSummary"] = relationship(
        back_populates="items",
        lazy="raise",
    )

    __table_args__ = (
        PrimaryKeyConstraint("purchase_summary_id", "product_id"),
        ForeignKeyConstraint(["purchase_summary_id"], ["purchase_summary.entity_id"]),
        ForeignKeyConstraint(["product_id"], ["product.entity_id"]),
    )
