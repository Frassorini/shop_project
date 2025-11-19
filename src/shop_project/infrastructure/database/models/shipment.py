from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import Mapped, relationship

from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class Shipment(Base):
    __tablename__ = "shipment"

    entity_id = Column(UUIDBinary(), nullable=False)
    state = Column(String(50), nullable=False)

    items: Mapped[list["ShipmentItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)


class ShipmentItem(Base):
    __tablename__ = "shipment_item"

    shipment_id = Column(UUIDBinary(), nullable=False)
    product_id = Column(UUIDBinary(), nullable=False)
    amount = Column(Integer(), nullable=False)

    order: Mapped["Shipment"] = relationship(
        back_populates="items",
        lazy="raise",
    )

    __table_args__ = (
        PrimaryKeyConstraint("shipment_id", "product_id"),
        ForeignKeyConstraint(["shipment_id"], ["shipment.entity_id"]),
        ForeignKeyConstraint(["product_id"], ["product.entity_id"]),
    )
