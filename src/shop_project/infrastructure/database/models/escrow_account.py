from sqlalchemy import Column, Numeric, PrimaryKeyConstraint, String

from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class EscrowAccount(Base):
    __tablename__ = "escrow_account"

    entity_id = Column(UUIDBinary(), nullable=False)
    total_amount = Column(Numeric(), nullable=False)
    state = Column(String(50), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)
