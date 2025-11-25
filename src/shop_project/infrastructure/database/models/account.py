from sqlalchemy import Column, PrimaryKeyConstraint, String

from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class Account(Base):
    __tablename__ = "account"

    entity_id = Column(UUIDBinary(), nullable=False)
    subject_type = Column(String(50), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)
