from sqlalchemy import Column, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String
from shop_project.infrastructure.database.models.base import Base


class Cart(Base):
    __tablename__ = 'cart'
    
    entity_id = Column(Integer(), nullable=False)
    customer_id = Column(Integer(), nullable=False)
    store_id = Column(Integer(), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('entity_id'),
        ForeignKeyConstraint(['store_id'], ['store.entity_id']),
    )
    
    
class CartItem(Base):
    __tablename__ = 'cart_item'
    
    cart_id = Column(Integer(), nullable=False)
    store_item_id = Column(Integer(), nullable=False)
    amount = Column(Integer(), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('cart_id', 'store_item_id'),
        ForeignKeyConstraint(['cart_id'], ['cart.entity_id']),
        ForeignKeyConstraint(['store_item_id'], ['store_item.entity_id']),
    )