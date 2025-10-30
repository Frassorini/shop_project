from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, relationship
from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class ShipmentSummary(Base):
    __tablename__ = 'shipment_summary'
    
    entity_id = Column(UUIDBinary(), nullable=False)
    reason = Column(String(50), nullable=False)
    
    items: Mapped[list["ShipmentSummaryItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('entity_id'),
    )
    
    
class ShipmentSummaryItem(Base):
    __tablename__ = 'shipment_summary_item'
    
    shipment_summary_id = Column(UUIDBinary(), nullable=False)
    store_item_id = Column(UUIDBinary(), nullable=False)
    amount = Column(Integer(), nullable=False)
    
    order: Mapped["ShipmentSummary"] = relationship(
        back_populates="items",
        lazy="raise",
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('shipment_summary_id', 'store_item_id'),
        ForeignKeyConstraint(['shipment_summary_id'], ['shipment_summary.entity_id']),
        ForeignKeyConstraint(['store_item_id'], ['store_item.entity_id']),
    )