from typing import Protocol


class EntropySource(Protocol):
    def generate_bytes(self, num_bytes: int) -> bytes: ...
