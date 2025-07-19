from sqlalchemy import Column, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String
from shop_project.infrastructure.database.models.base import Base


class CustomerOrder(Base):
    __tablename__ = 'customer_order'
    
    entity_id = Column(Integer(), nullable=False)
    customer_id = Column(Integer(), nullable=False)
    store_id = Column(Integer(), nullable=False)
    state = Column(String(50), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('entity_id'),
        ForeignKeyConstraint(['store_id'], ['store.entity_id']),
    )
    
    
class CustomerOrderItem(Base):
    __tablename__ = 'customer_order_item'
    
    customer_order_id = Column(Integer(), nullable=False)
    store_item_id = Column(Integer(), nullable=False)
    amount = Column(Integer(), nullable=False)
    price = Column(Numeric(), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('customer_order_id', 'store_item_id'),
        ForeignKeyConstraint(['customer_order_id'], ['customer_order.entity_id']),
        ForeignKeyConstraint(['store_item_id'], ['store_item.entity_id']),
    )