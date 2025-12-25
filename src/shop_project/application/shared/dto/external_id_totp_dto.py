from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import SecretStr

from shop_project.application.shared.base_dto import BaseDTO
from shop_project.infrastructure.entities.external_id_totp import ExternalIdTotp


class ExternalIdTotpDTO(BaseDTO[ExternalIdTotp]):
    entity_id: UUID
    external_id_type: str
    external_id: str
    totp_verifier: SecretStr
    issued_at: datetime
    expiration: datetime

    @classmethod
    def to_dto(cls, domain_object: ExternalIdTotp) -> Self:
        return cls(
            entity_id=domain_object.entity_id,
            external_id_type=domain_object.external_id_type,
            external_id=domain_object.external_id,
            totp_verifier=domain_object.totp_verifier,
            issued_at=domain_object.issued_at,
            expiration=domain_object.expiration,
        )

    def to_domain(self) -> ExternalIdTotp:
        return ExternalIdTotp.load(
            entity_id=self.entity_id,
            external_id_type=self.external_id_type,
            external_id=self.external_id,
            totp_verifier=self.totp_verifier,
            issued_at=self.issued_at,
            expiration=self.expiration,
        )
