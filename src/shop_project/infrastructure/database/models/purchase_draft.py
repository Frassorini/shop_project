from sqlalchemy import Column, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, relationship
from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class PurchaseDraft(Base):
    __tablename__ = 'purchase_draft'
    
    entity_id = Column(UUIDBinary(), nullable=False)
    customer_id = Column(UUIDBinary(), nullable=False)
    state = Column(String(50), nullable=False)
    
    items: Mapped[list["PurchaseDraftItem"]] = relationship(
        back_populates="purchase_draft",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('entity_id'),
    )
    
    
class PurchaseDraftItem(Base):
    __tablename__ = 'purchase_draft_item'
    
    purchase_draft_id = Column(UUIDBinary(), nullable=False)
    product_id = Column(UUIDBinary(), nullable=False)
    amount = Column(Integer(), nullable=False)
    
    purchase_draft: Mapped["PurchaseDraft"] = relationship(
        back_populates="items",
        lazy="raise",
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('purchase_draft_id', 'product_id'),
        ForeignKeyConstraint(['purchase_draft_id'], ['purchase_draft.entity_id']),
        ForeignKeyConstraint(['product_id'], ['product.entity_id']),
    )