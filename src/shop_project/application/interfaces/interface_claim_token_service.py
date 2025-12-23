from typing import Protocol
from uuid import UUID

from shop_project.infrastructure.entities.claim_token import ClaimToken


class IClaimTokenService(Protocol):
    def get_claim_token_fingerprint(self, claim_token: str) -> str: ...

    def refresh(self) -> str: ...

    def create(self, customer_id: UUID) -> tuple[ClaimToken, str]: ...

    def verify(self, claim_token: ClaimToken, raw_token: str) -> bool: ...
