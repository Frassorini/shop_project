from typing import Any
from uuid import UUID

from pydantic import SecretStr
from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from shop_project.infrastructure.database.models.base import Base


class Account(Base):
    __tablename__ = "account"

    entity_id: Mapped[UUID] = mapped_column(nullable=False)
    subject_type: Mapped[str] = mapped_column(String(50), nullable=False)
    password_verifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    login: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (PrimaryKeyConstraint("entity_id"),)

    def repopulate(
        self,
        entity_id: UUID,
        subject_type: str,
        password_verifier: SecretStr | None,
        login: str | None,
        phone_number: str | None,
        email: str | None,
        **kw: Any,
    ) -> None:
        self.entity_id = entity_id
        self.subject_type = subject_type
        self.password_verifier = (
            password_verifier.get_secret_value() if password_verifier else None
        )
        self.login = login
        self.phone_number = phone_number
        self.email = email

    def __init__(self, **kw: Any) -> None:
        super().__init__()
        self.repopulate(**kw)
