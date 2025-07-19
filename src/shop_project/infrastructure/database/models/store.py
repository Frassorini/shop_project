from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String
from shop_project.infrastructure.database.models.base import Base


class Store(Base):
    __tablename__ = 'store'
    
    entity_id = Column(Integer(), nullable=False)
    name = Column(String(50), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('entity_id'),
    )