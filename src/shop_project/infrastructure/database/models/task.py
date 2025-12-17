from typing import Any
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from shop_project.infrastructure.database.models.base import Base


class Task(Base):
    __tablename__ = "task"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    handler: Mapped[str] = mapped_column(String(50), nullable=False)
    params_json: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)

    def repopulate(
        self,
        entity_id: UUID,
        handler: str,
        params_json: str,
    ) -> None:
        self.entity_id = entity_id
        self.handler = handler
        self.params_json = params_json

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)
