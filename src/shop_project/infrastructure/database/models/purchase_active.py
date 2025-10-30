from sqlalchemy import Column, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, relationship
from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.models.escrow_account import EscrowAccount
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class PurchaseActive(Base):
    __tablename__ = 'purchase_active'
    
    entity_id = Column(UUIDBinary(), nullable=False)
    customer_id = Column(UUIDBinary(), nullable=False)
    escrow_account_id = Column(UUIDBinary(), nullable=False)
    state = Column(String(50), nullable=False)
    
    items: Mapped[list["PurchaseActiveItem"]] = relationship(
        back_populates="purchase_active",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    
    escrow_account: Mapped["EscrowAccount"] = relationship(
        lazy="raise",
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('entity_id'),
        ForeignKeyConstraint(['escrow_account_id'], ['escrow_account.entity_id']),
    )
    
    
class PurchaseActiveItem(Base):
    __tablename__ = 'purchase_active_item'
    
    purchase_active_id = Column(UUIDBinary(), nullable=False)
    product_id = Column(UUIDBinary(), nullable=False)
    amount = Column(Integer(), nullable=False)
    
    purchase_active: Mapped["PurchaseActive"] = relationship(
        back_populates="items",
        lazy="raise",
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('purchase_active_id', 'product_id'),
        ForeignKeyConstraint(['purchase_active_id'], ['purchase_active.entity_id']),
        ForeignKeyConstraint(['product_id'], ['product.entity_id']),
    )