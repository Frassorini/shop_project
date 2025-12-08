from typing import Protocol


class TokenFingerprintCalculator(Protocol):
    """Interface for calculating deterministic token fingerprints."""

    def fingerprint(self, token: str) -> str: ...
