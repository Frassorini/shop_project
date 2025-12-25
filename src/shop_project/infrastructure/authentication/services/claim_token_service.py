from datetime import datetime, timedelta, timezone
from uuid import UUID

from shop_project.application.shared.interfaces.interface_claim_token_service import (
    IClaimTokenService,
)
from shop_project.infrastructure.cryptography.interfaces.token_fingerprint_calculator import (
    TokenFingerprintCalculator,
)
from shop_project.infrastructure.cryptography.interfaces.token_generator import (
    TokenGenerator,
)
from shop_project.infrastructure.entities.claim_token import ClaimToken


class ClaimTokenService(IClaimTokenService):
    def __init__(
        self,
        token_fingerprint_calculator: TokenFingerprintCalculator,
        rand_datagen: TokenGenerator,
        token_ttl: timedelta,
    ) -> None:
        self.token_fingerprint_calculator = token_fingerprint_calculator
        self.rand_datagen = rand_datagen
        self.token_ttl = token_ttl

    def get_claim_token_fingerprint(self, claim_token: str) -> str:
        return self.token_fingerprint_calculator.fingerprint(claim_token)

    def refresh(self) -> str:
        raw_token = self.rand_datagen.generate()

        self.token_fingerprint_calculator.fingerprint(raw_token)

        return raw_token

    def create(self, customer_id: UUID) -> tuple[ClaimToken, str]:
        raw_token = self.rand_datagen.generate()

        return (
            ClaimToken(
                entity_id=customer_id,
                token_fingerprint=self.token_fingerprint_calculator.fingerprint(
                    raw_token
                ),
                issued_at=datetime.now(tz=timezone.utc),
                expiration=datetime.now(tz=timezone.utc) + self.token_ttl,
            ),
            raw_token,
        )

    def verify(self, claim_token: ClaimToken, raw_token: str) -> bool:
        if (
            not self.token_fingerprint_calculator.fingerprint(raw_token)
            == claim_token.token_fingerprint
        ):
            return False
        if not claim_token.expiration > datetime.now(tz=timezone.utc):
            return False
        return True
