from sqlalchemy import Column, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String
from shop_project.infrastructure.database.models.base import Base


class StoreItem(Base):
    __tablename__ = 'store_item'
    
    entity_id = Column(Integer(), nullable=False)
    store_id = Column(Integer(), nullable=False)
    name = Column(String(50), nullable=False)
    amount = Column(Integer(), nullable=False)
    price = Column(Numeric(), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('entity_id'),
        ForeignKeyConstraint(['store_id'], ['store.entity_id']),
    )