from abc import ABC
from typing import Any, Literal, Sequence, Type, TypeVar, cast

from shop_project.domain.cart import Cart
from shop_project.domain.customer import Customer
from shop_project.domain.p_aggregate import PAggregate
from shop_project.domain.store import Store
from shop_project.domain.supplier_order import SupplierOrder
from shop_project.shared.entity_id import EntityId

from shop_project.infrastructure.resource_manager.resource_snapshot import ResourceSnapshot, EntitySnapshot, EntitySnapshotSet
from shop_project.exceptions import ResourcesException

from shop_project.domain.customer_order import CustomerOrder
from shop_project.domain.store_item import StoreItem


T = TypeVar('T', bound=PAggregate)


class ResourceSnapshotSentinelMixin(ABC):
    resources: dict[Type[PAggregate], list[PAggregate]]
    _resource_snapshot_previous: ResourceSnapshot | None
    _resource_snapshot_current: ResourceSnapshot | None
    
    def _get_resource_snapshot(self) -> ResourceSnapshot:
        snapshot_set_vector: dict[Type[PAggregate], EntitySnapshotSet] = {}
        for resource_type in self.resources:
            snapshot_set_vector[resource_type] = EntitySnapshotSet([EntitySnapshot(item.snapshot()) for item in self.resources[resource_type]])
        
        return ResourceSnapshot(snapshot_set_vector)
    
    def take_snapshot(self) -> None:
        if self._resource_snapshot_previous is not None:
            raise RuntimeError("Snapshots are already taken")
        
        self._resource_snapshot_previous = self._resource_snapshot_current
        self._resource_snapshot_current = self._get_resource_snapshot()
    
    def get_resource_changes(self) -> dict[Type[PAggregate], dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[dict[str, Any]]]]:
        if self._resource_snapshot_current is None or self._resource_snapshot_previous is None:
            raise RuntimeError("Snapshots are not taken yet")
        
        deleted_snapshot: ResourceSnapshot = self._resource_snapshot_previous.difference_identity(self._resource_snapshot_current)
        created_snapshot: ResourceSnapshot = self._resource_snapshot_current.difference_identity(self._resource_snapshot_previous)
        current_snapshot_side_intersection: ResourceSnapshot = self._resource_snapshot_current.intersect_identity(self._resource_snapshot_previous)
        updated_snapshot: ResourceSnapshot = current_snapshot_side_intersection.difference_content(self._resource_snapshot_previous)
        
        result: dict[Type[PAggregate], dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[dict[str, Any]]]] = {}
        for item_type in self.resources.keys():
            result[item_type] = {
                'CREATED': [],
                'UPDATED': [],
                'DELETED': [],
            }
        
        for item_type, items in deleted_snapshot.to_dict().items():
            result[item_type]['DELETED'].extend(items)
            
        for item_type, items in updated_snapshot.to_dict().items():
            result[item_type]['UPDATED'].extend(items)
        
        for item_type, items in created_snapshot.to_dict().items():
            result[item_type]['CREATED'].extend(items)
        
        return result
        
class ResourceContainer(ResourceSnapshotSentinelMixin):
    def __init__(self):
        self.resources: dict[Type[PAggregate], list[PAggregate]] = { 
            Customer: [],
            CustomerOrder: [],
            SupplierOrder: [],
            Cart: [],
            StoreItem: [],
            Store: [],
        }
        self._resource_snapshot_previous: ResourceSnapshot | None = None
        self._resource_snapshot_current: ResourceSnapshot | None = None
    
    def _get_resource_by_type(self, resource_type: Type[T]) -> list[T]:
        if resource_type in self.resources:
            return cast(list[T], self.resources[resource_type])
        raise NotImplementedError(f"No resource for {resource_type}")
    
    def get_by_attribute(self, model_type: Type[T], 
                         attribute_name: str, 
                         values: list[Any]) -> list[T]:
        
        resource = self._get_resource_by_type(model_type)
        
        result: list[T] = []
        for item in resource:
            if getattr(item, attribute_name) in values:
                result.append(item)
        return result
    
    def get_by_id(self, model_type: Type[T], entity_id: EntityId) -> T:
        result: list[T] = self.get_by_attribute(model_type, "entity_id", [entity_id])

        if not result:
            raise ResourcesException(f"Could not find {model_type} with id {entity_id}")
        
        if len(result) > 1:
            raise RuntimeError(f"Found more than one {model_type} with id {entity_id}")

        return result[0]
    
    def get_all(self, model_type: Type[T]) -> Sequence[T]:
        return self._get_resource_by_type(model_type).copy()
    
    def put(self, model_type: Type[PAggregate], item: PAggregate) -> None:
        self._get_resource_by_type(model_type).append(item)
        
    def put_many(self, model_type: Type[PAggregate], items: list[PAggregate]) -> None:
        self._get_resource_by_type(model_type).extend(items)
    
    def delete(self, model_type: Type[PAggregate], item: PAggregate) -> None:
        self._get_resource_by_type(model_type).remove(item)
    
    def delete_many(self, model_type: Type[PAggregate], items: Sequence[PAggregate]) -> None:
        for item in items:
            self.delete(model_type, item)