from sqlalchemy import Column, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, relationship
from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class PurchaseDraft(Base):
    __tablename__ = 'cart'
    
    entity_id = Column(UUIDBinary(), nullable=False)
    customer_id = Column(UUIDBinary(), nullable=False)
    
    items: Mapped[list["PurchaseDraftItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('entity_id'),
    )
    
    
class PurchaseDraftItem(Base):
    __tablename__ = 'cart_item'
    
    cart_id = Column(UUIDBinary(), nullable=False)
    store_item_id = Column(UUIDBinary(), nullable=False)
    amount = Column(Integer(), nullable=False)
    
    order: Mapped["PurchaseDraft"] = relationship(
        back_populates="items",
        lazy="raise",
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('cart_id', 'store_item_id'),
        ForeignKeyConstraint(['cart_id'], ['cart.entity_id']),
        ForeignKeyConstraint(['store_item_id'], ['store_item.entity_id']),
    )