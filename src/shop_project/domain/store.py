from typing import Any, Self
from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.shared.entity_id import EntityId
from shop_project.shared.identity_mixin import IdentityMixin
from shop_project.shared.p_snapshotable import PSnapshotable


class Store(BaseAggregate):
    def __init__(self, entity_id: EntityId, name: str) -> None:
        self._entity_id: EntityId = entity_id
        self.name: str = name
    
    def to_dict(self) -> dict[str, Any]:
        return {'entity_id': self.entity_id.value, 'name': self.name}
    
    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(EntityId(snapshot['entity_id']), snapshot['name'])