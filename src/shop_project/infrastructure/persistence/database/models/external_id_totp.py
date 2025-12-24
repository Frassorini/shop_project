from typing import Any
from uuid import UUID

from pydantic import SecretStr
from sqlalchemy import DateTime, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from shop_project.infrastructure.persistence.database.models.base import Base


class ExternalIdTotp(Base):
    __tablename__ = "external_id_totp"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    external_id_type: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(50), nullable=False)
    totp_verifier: Mapped[str] = mapped_column(String(255), nullable=False)
    issued_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    expiration: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)

    def repopulate(
        self,
        entity_id: UUID,
        external_id_type: str,
        external_id: str,
        totp_verifier: SecretStr,
        issued_at: DateTime,
        expiration: DateTime,
        **kw: Any,
    ) -> None:
        self.entity_id = entity_id
        self.external_id_type = external_id_type
        self.external_id = external_id
        self.totp_verifier = totp_verifier.get_secret_value()
        self.issued_at = issued_at
        self.expiration = expiration

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)
