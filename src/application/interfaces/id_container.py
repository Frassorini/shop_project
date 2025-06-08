from application.interfaces.p_criteria_provider import PCriteriaProvider
from shared.entity_id import EntityId


class IdContainer(PCriteriaProvider):
    def __init__(self, entity_ids: list[EntityId]) -> None:
        self._entity_ids = entity_ids
        
    def extract(self) -> list[EntityId]:
        return self._entity_ids