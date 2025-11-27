from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shop_project.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from shop_project.infrastructure.database.models.account import Account


class Employee(Base):
    __tablename__ = "employee"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    account: Mapped["Account"] = relationship(
        lazy="raise",
    )

    __table_args__ = (
        PrimaryKeyConstraint("entity_id"),
        ForeignKeyConstraint(["entity_id"], ["account.entity_id"]),
    )

    def repopulate(self, entity_id: UUID, name: str, **kw: Any) -> None:
        self.entity_id = entity_id
        self.name = name

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)
