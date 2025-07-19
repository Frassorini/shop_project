from typing import Self
from shop_project.shared.identity_mixin import IdentityMixin
from shop_project.shared.entity_id import EntityId
from shop_project.shared.p_snapshotable import PSnapshotable


class Customer(IdentityMixin, PSnapshotable):
    def __init__(self, entity_id: EntityId, name: str) -> None:
        self._entity_id: EntityId = entity_id
        self.name: str = name
        
    def snapshot(self) -> dict[str, str]:
        return {'entity_id': self.entity_id.to_str(), 'name': self.name}
    
    @classmethod
    def from_snapshot(cls, snapshot: dict[str, str]) -> Self:
        return cls(EntityId(snapshot['entity_id']), snapshot['name'])