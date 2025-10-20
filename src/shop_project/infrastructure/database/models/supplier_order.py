from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, relationship
from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class SupplierOrder(Base):
    __tablename__ = 'supplier_order'
    
    entity_id = Column(UUIDBinary(), nullable=False)
    departure = Column(DateTime(timezone=True), nullable=False)
    arrival = Column(DateTime(timezone=True), nullable=False)
    state = Column(String(50), nullable=False)
    
    items: Mapped[list["SupplierOrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('entity_id'),
    )
    
    
class SupplierOrderItem(Base):
    __tablename__ = 'supplier_order_item'
    
    supplier_order_id = Column(UUIDBinary(), nullable=False)
    store_item_id = Column(UUIDBinary(), nullable=False)
    amount = Column(Integer(), nullable=False)
    
    order: Mapped["SupplierOrder"] = relationship(
        back_populates="items",
        lazy="raise",
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('supplier_order_id', 'store_item_id'),
        ForeignKeyConstraint(['supplier_order_id'], ['supplier_order.entity_id']),
        ForeignKeyConstraint(['store_item_id'], ['store_item.entity_id']),
    )