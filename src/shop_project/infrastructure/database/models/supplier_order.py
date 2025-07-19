from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String
from shop_project.infrastructure.database.models.base import Base


class SupplierOrder(Base):
    __tablename__ = 'supplier_order'
    
    entity_id = Column(Integer(), nullable=False)
    departure = Column(DateTime(timezone=True), nullable=False)
    arrival = Column(DateTime(timezone=True), nullable=False)
    store_id = Column(Integer(), nullable=False)
    state = Column(String(50), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('entity_id'),
        ForeignKeyConstraint(['store_id'], ['store.entity_id']),
    )
    
    
class SupplierOrderItem(Base):
    __tablename__ = 'supplier_order_item'
    
    supplier_order_id = Column(Integer(), nullable=False)
    store_item_id = Column(Integer(), nullable=False)
    amount = Column(Integer(), nullable=False)
    price = Column(Integer(), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('supplier_order_id', 'store_item_id'),
        ForeignKeyConstraint(['supplier_order_id'], ['customer_order.entity_id']),
        ForeignKeyConstraint(['store_item_id'], ['store_item.entity_id']),
    )