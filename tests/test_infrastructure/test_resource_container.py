from typing import Callable
from uuid import uuid4

import pytest
from shop_project.exceptions import ResourcesException
from shop_project.infrastructure.resource_manager.resource_manager import ResourceContainer
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.shared.entity_id import EntityId
from shop_project.application.dto.mapper import to_dto

from shop_project.infrastructure.registries.resources_registry import ResourcesRegistry


def test_get_by_id(purchase_draft_factory: Callable[[], PurchaseDraft]) -> None:
    container = ResourceContainer(resources_registry=ResourcesRegistry.get_map())
    purchase_draft = purchase_draft_factory()
    
    container.put(PurchaseDraft, purchase_draft)
    
    assert container.get_by_id(PurchaseDraft, purchase_draft.entity_id) == purchase_draft


def test_get_by_attribute(purchase_draft_factory: Callable[[], PurchaseDraft]) -> None:
    container = ResourceContainer(resources_registry=ResourcesRegistry.get_map())
    purchase_draft_1 = purchase_draft_factory()
    purchase_draft_2 = purchase_draft_factory()
    
    container.put(PurchaseDraft, purchase_draft_1)
    container.put(PurchaseDraft, purchase_draft_2)

    assert container.get_by_attribute(PurchaseDraft, "entity_id", [purchase_draft_1.entity_id, purchase_draft_2.entity_id]) == [purchase_draft_1, purchase_draft_2]
    assert container.get_by_attribute(PurchaseDraft, "customer_id", [purchase_draft_1.customer_id]) == [purchase_draft_1]
    

def test_get_by_wrong_attribute(purchase_draft_factory: Callable[[], PurchaseDraft]) -> None:
    container = ResourceContainer(resources_registry=ResourcesRegistry.get_map())
    purchase_draft_1 = purchase_draft_factory()
    
    container.put(PurchaseDraft, purchase_draft_1)

    with pytest.raises(AttributeError):
        container.get_by_attribute(PurchaseDraft, "wrong_attribute", [purchase_draft_1.entity_id])


def test_get_by_id_not_found(purchase_draft_factory: Callable[[], PurchaseDraft]) -> None:
    container = ResourceContainer(resources_registry=ResourcesRegistry.get_map())
    purchase_draft_1 = purchase_draft_factory()
    
    container.put(PurchaseDraft, purchase_draft_1)

    with pytest.raises(ResourcesException):
        container.get_by_id(PurchaseDraft, EntityId(uuid4()))


def test_snapshot_create(purchase_draft_factory: Callable[[], PurchaseDraft]) -> None:
    container = ResourceContainer(resources_registry=ResourcesRegistry.get_map())
    container.take_snapshot()
    purchase_draft = purchase_draft_factory()
    
    container.put(PurchaseDraft, purchase_draft)

    container.take_snapshot()
    
    assert to_dto(purchase_draft) in container.get_resource_changes()[PurchaseDraft]['CREATED']


def test_snapshot_delete(purchase_draft_factory: Callable[[], PurchaseDraft]) -> None:
    container = ResourceContainer(resources_registry=ResourcesRegistry.get_map())
    purchase_draft = purchase_draft_factory()
    
    container.put(PurchaseDraft, purchase_draft)
    container.take_snapshot()
    container.delete(PurchaseDraft, purchase_draft)
    container.take_snapshot()

    
    assert to_dto(purchase_draft) in container.get_resource_changes()[PurchaseDraft]['DELETED']


def test_snapshot_update(purchase_draft_factory: Callable[[], PurchaseDraft]) -> None:
    container = ResourceContainer(resources_registry=ResourcesRegistry.get_map())
    purchase_draft: PurchaseDraft = purchase_draft_factory()
    
    container.put(PurchaseDraft, purchase_draft)
    container.take_snapshot()
    purchase_draft.finalize()
    container.take_snapshot()
    
    assert to_dto(purchase_draft) in container.get_resource_changes()[PurchaseDraft]['UPDATED']


def test_snapshot_no_previous(purchase_draft_factory: Callable[[], PurchaseDraft]) -> None:
    container = ResourceContainer(resources_registry=ResourcesRegistry.get_map())
    purchase_draft_1 = purchase_draft_factory()
    
    container.put(PurchaseDraft, purchase_draft_1)

    container.take_snapshot()
    
    with pytest.raises(RuntimeError):
        container.get_resource_changes()


def test_too_many_snapshots() -> None:
    container = ResourceContainer(resources_registry=ResourcesRegistry.get_map())
    container.take_snapshot()

    container.take_snapshot()
    
    with pytest.raises(RuntimeError):
        container.take_snapshot()