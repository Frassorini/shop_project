from typing import Callable
import pytest

from shop_project.domain.exceptions import DomainException
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.services.purchase_activation_service import PurchaseActivationService
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.store_item import StoreItem
from shop_project.domain.purchase_active import PurchaseActive


def test_(potatoes_store_item_10: Callable[[], StoreItem], 
          purchase_activation_service_factory: Callable[[InventoryService], PurchaseActivationService]) -> None:
    potatoes = potatoes_store_item_10()
    inventory_service = InventoryService([potatoes])
    purchase_activation_service = purchase_activation_service_factory(inventory_service)


def test_activate(purchase_draft_factory: Callable[[], PurchaseDraft],
                  potatoes_store_item_10: Callable[[], StoreItem],
                  purchase_activation_service_factory: Callable[[InventoryService], PurchaseActivationService]) -> None:
    potatoes = potatoes_store_item_10()
    purchase_draft = purchase_draft_factory()
    purchase_draft.add_item(store_item_id=potatoes.entity_id, amount=2)
    inventory_service = InventoryService([potatoes])
    purchase_activation_service = purchase_activation_service_factory(inventory_service)

    activation = purchase_activation_service.activate(purchase_draft)

    assert potatoes.amount == 8
    assert activation.escrow_account.is_pending()
    assert activation.purchase_active.get_items()[0].amount == 2


def test_activate_twice(purchase_draft_factory: Callable[[], PurchaseDraft],
                              potatoes_store_item_10: Callable[[], StoreItem],
                              purchase_activation_service_factory: Callable[[InventoryService], PurchaseActivationService]) -> None:
    potatoes = potatoes_store_item_10()
    purchase_draft = purchase_draft_factory()
    purchase_draft.add_item(store_item_id=potatoes.entity_id, amount=2)
    inventory_service = InventoryService([potatoes])
    purchase_activation_service = purchase_activation_service_factory(inventory_service)
    
    activation = purchase_activation_service.activate(purchase_draft)

    with pytest.raises(DomainException):
        purchase_activation_service.activate(purchase_draft)
