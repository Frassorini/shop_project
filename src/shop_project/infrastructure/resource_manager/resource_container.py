from abc import ABC
from typing import Any, Literal, Sequence, Type, TypeVar, cast

from shop_project.shared.entity_id import EntityId

from shop_project.application.dto.base_dto import BaseDTO
from shop_project.application.dto.mapper import to_dto

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.purchase_summary import PurchaseSummary
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment
from shop_project.domain.shipment_summary import ShipmentSummary

from shop_project.infrastructure.resource_manager.resource_snapshot import ResourceSnapshot, EntitySnapshot, EntitySnapshotSet

from shop_project.infrastructure.exceptions import ResourcesException


T = TypeVar('T', bound=BaseAggregate)


class ResourceSnapshotSentinelMixin(ABC):
    resources: dict[Type[BaseAggregate], list[BaseAggregate]]
    _resource_snapshot_previous: ResourceSnapshot | None
    _resource_snapshot_current: ResourceSnapshot | None
    
    def _get_resource_snapshot(self) -> ResourceSnapshot:
        snapshot_set_vector: dict[Type[BaseAggregate], EntitySnapshotSet] = {}
        for resource_type in self.resources:
            snapshot_set_vector[resource_type] = EntitySnapshotSet([EntitySnapshot(to_dto(item)) for item in self.resources[resource_type]])
        
        return ResourceSnapshot(snapshot_set_vector)
    
    def take_snapshot(self) -> None:
        if self._resource_snapshot_previous is not None:
            raise RuntimeError("Snapshots are already taken")
        
        self._resource_snapshot_previous = self._resource_snapshot_current
        self._resource_snapshot_current = self._get_resource_snapshot()
    
    def get_resource_changes(self) -> dict[Type[BaseAggregate], dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[BaseDTO]]]:
        if self._resource_snapshot_current is None or self._resource_snapshot_previous is None:
            raise RuntimeError("Snapshots are not taken yet")
        
        deleted_snapshot: ResourceSnapshot = self._resource_snapshot_previous.difference_identity(self._resource_snapshot_current)
        created_snapshot: ResourceSnapshot = self._resource_snapshot_current.difference_identity(self._resource_snapshot_previous)
        current_snapshot_side_intersection: ResourceSnapshot = self._resource_snapshot_current.intersect_identity(self._resource_snapshot_previous)
        updated_snapshot: ResourceSnapshot = current_snapshot_side_intersection.difference_content(self._resource_snapshot_previous)
        
        result: dict[Type[BaseAggregate], dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[BaseDTO]]] = {}
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
    def __init__(self, resources_registry: list[Type[BaseAggregate]]):
        self.resources: dict[Type[BaseAggregate], list[BaseAggregate]] = { 
            resource: [] for resource in resources_registry
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
    
    def put(self, model_type: Type[BaseAggregate], item: BaseAggregate) -> None:
        self._get_resource_by_type(model_type).append(item)
        
    def put_many(self, model_type: Type[BaseAggregate], items: list[BaseAggregate]) -> None:
        self._get_resource_by_type(model_type).extend(items)
    
    def delete(self, model_type: Type[BaseAggregate], item: BaseAggregate) -> None:
        self._get_resource_by_type(model_type).remove(item)
    
    def delete_many(self, model_type: Type[BaseAggregate], items: Sequence[BaseAggregate]) -> None:
        for item in items:
            self.delete(model_type, item)