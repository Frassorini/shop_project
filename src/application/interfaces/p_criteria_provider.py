from typing import Protocol

from shared.entity_id import EntityId


class PCriteriaProvider(Protocol):
    def extract(self) -> list[EntityId]:
        ...