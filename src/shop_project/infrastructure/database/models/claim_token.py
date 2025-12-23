from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import (
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shop_project.infrastructure.database.models.base import Base
from shop_project.infrastructure.database.models.customer import Customer
from shop_project.infrastructure.database.utc_datetime import UTCDateTime

if TYPE_CHECKING:
    pass


class ClaimToken(Base):
    __tablename__ = "claim_token"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    token_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False
    )
    expiration: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False
    )

    customer: Mapped["Customer"] = relationship(
        lazy="raise",
    )

    __table_args__ = (
        PrimaryKeyConstraint("entity_id"),
        ForeignKeyConstraint(["entity_id"], ["customer.entity_id"]),
    )

    def repopulate(
        self,
        entity_id: UUID,
        token_fingerprint: str,
        issued_at: datetime,
        expiration: datetime,
        **kw: Any,
    ) -> None:
        self.entity_id = entity_id
        self.token_fingerprint = token_fingerprint
        self.issued_at = issued_at
        self.expiration = expiration

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)
