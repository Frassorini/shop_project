from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from shop_project.infrastructure.persistence.database.models.base import Base
from shop_project.infrastructure.persistence.database.seq_type import SeqType
from shop_project.infrastructure.persistence.database.utc_datetime import UTCDateTime


class OperationLog(Base):
    __tablename__ = "operation_log"

    entity_id: Mapped[UUID] = mapped_column(nullable=False, unique=True)
    seq: Mapped[int] = mapped_column(
        SeqType(), nullable=False, autoincrement=True, unique=True
    )  # let database generate on its own
    operation_code: Mapped[str] = mapped_column(String(50), nullable=False)
    payload_json: Mapped[str] = mapped_column(String(255), nullable=False)
    occured_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True), nullable=False
    )

    __table_args__ = (PrimaryKeyConstraint("seq"),)

    def repopulate(
        self,
        entity_id: UUID,
        operation_code: str,
        payload_json: str,
        occured_at: datetime,
        seq: int,
    ) -> None:
        self.entity_id = entity_id
        self.operation_code = operation_code
        self.payload_json = payload_json
        self.occured_at = occured_at

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)
