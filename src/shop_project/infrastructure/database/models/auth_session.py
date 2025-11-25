from sqlalchemy import Column, DateTime, PrimaryKeyConstraint, String

from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class CustomerSession(Base):
    __tablename__ = "customer_session"

    entity_id = Column(UUIDBinary(), nullable=False)
    refresh_token = Column(String(255), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)


class EmployeeSession(Base):
    __tablename__ = "employee_session"

    entity_id = Column(UUIDBinary(), nullable=False)
    refresh_token = Column(String(255), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)


class ManagerSession(Base):
    __tablename__ = "manager_session"

    entity_id = Column(UUIDBinary(), nullable=False)
    refresh_token = Column(String(255), nullable=False)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)
