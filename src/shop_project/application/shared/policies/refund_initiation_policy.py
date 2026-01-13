from dataclasses import dataclass


@dataclass(frozen=True)
class RefundInitiationPolicy:
    start_immediately: bool
