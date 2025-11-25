from sqlalchemy import Column, PrimaryKeyConstraint, String

from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.uuid_binary import UUIDBinary


class CustomerSecret(Base):
    __tablename__ = "customer_secret"

    entity_id = Column(UUIDBinary(), nullable=False)
    auth_type = Column(String(50), nullable=False)
    payload = Column(String(255), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)


class ManagerSecret(Base):
    __tablename__ = "manager_secret"

    entity_id = Column(UUIDBinary(), nullable=False)
    auth_type = Column(String(50), nullable=False)
    payload = Column(String(255), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)


class EmployeeSecret(Base):
    __tablename__ = "employee_secret"

    entity_id = Column(UUIDBinary(), nullable=False)
    auth_type = Column(String(50), nullable=False)
    payload = Column(String(255), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)
