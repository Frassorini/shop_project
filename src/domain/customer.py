from typing import Any, Self
from domain.p_aggregate import PAggregate
from shared.identity_mixin import IdentityMixin
from shared.entity_id import EntityId
from shared.p_snapshotable import PSnapshotable


class Customer(IdentityMixin, PSnapshotable):
    def __init__(self, entity_id: EntityId, name: str) -> None:
        self._entity_id: EntityId = entity_id
        self.name: str = name
        
    def snapshot(self) -> dict[str, object]:
        return {'entity_id': self.entity_id.to_str(), 'name': self.name}
    
    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> Self:
        return cls(EntityId.from_str(snapshot['entity_id']), snapshot['name'])