from typing import Any
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from shop_project.infrastructure.database.models.base import Base


class Account(Base):
    __tablename__ = "account"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    subject_type: Mapped[str] = mapped_column(String(50), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)

    def repopulate(self, entity_id: UUID, subject_type: str, **kw: Any) -> None:
        self.entity_id = entity_id
        self.subject_type = subject_type

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)
