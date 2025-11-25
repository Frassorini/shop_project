from sqlalchemy import Column, ForeignKeyConstraint, PrimaryKeyConstraint, String

from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class Customer(Base):
    __tablename__ = "customer"

    entity_id = Column(UUIDBinary(), nullable=False)
    name = Column(String(50), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("entity_id"),
        ForeignKeyConstraint(["entity_id"], ["account.entity_id"]),
    )
