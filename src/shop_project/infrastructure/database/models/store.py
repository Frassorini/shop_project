from sqlalchemy import Column, Integer, PrimaryKeyConstraint, String
from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class Store(Base):
    __tablename__ = 'store'
    
    entity_id = Column(UUIDBinary(), nullable=False)
    name = Column(String(50), nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint('entity_id'),
    )