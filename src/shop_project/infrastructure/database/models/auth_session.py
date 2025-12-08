from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import SecretStr
from sqlalchemy import (
    DateTime,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shop_project.infrastructure.database.models.base import Base

if TYPE_CHECKING:
    from shop_project.infrastructure.database.models.account import Account


class AuthSession(Base):
    __tablename__ = "auth_session"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    account_id: Mapped[UUID] = mapped_column(nullable=False)
    refresh_token_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False)
    issued_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    expiration: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    account: Mapped["Account"] = relationship(
        lazy="raise",
    )

    __table_args__ = (
        PrimaryKeyConstraint("entity_id"),
        ForeignKeyConstraint(["account_id"], ["account.entity_id"]),
    )

    def repopulate(
        self,
        entity_id: UUID,
        account_id: UUID,
        refresh_token_fingerprint: SecretStr,
        issued_at: DateTime,
        expiration: DateTime,
        **kw: Any,
    ) -> None:
        self.entity_id = entity_id
        self.account_id = account_id
        self.refresh_token_fingerprint = refresh_token_fingerprint.get_secret_value()
        self.issued_at = issued_at
        self.expiration = expiration

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)
