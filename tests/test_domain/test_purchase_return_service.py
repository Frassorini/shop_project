from typing import Callable, cast
import pytest

from shop_project.domain.exceptions import DomainException
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_summary import PurchaseSummaryReason
from shop_project.domain.services.purchase_return_service import PurchaseReturnService
from shop_project.domain.services.inventory_service import InventoryService
from shop_project.domain.store_item import StoreItem
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.escrow_account import EscrowAccount
from tests.helpers import AggregateContainer


def test_(purchase_return_service_factory: Callable[[InventoryService], PurchaseReturnService],
          purchase_active_filled_container_factory: Callable[[], AggregateContainer]) -> None:
    container = purchase_active_filled_container_factory()
    inventory_service = InventoryService(container.dependencies[StoreItem])
    purchase_return_service = purchase_return_service_factory(inventory_service)


def test_purchase_cancel_payment(purchase_return_service_factory: Callable[[InventoryService], PurchaseReturnService],
                                 purchase_active_filled_container_factory: Callable[[], AggregateContainer]) -> None:
    container = purchase_active_filled_container_factory()
    inventory_service = InventoryService(container.dependencies[StoreItem])
    purchase_return_service = purchase_return_service_factory(inventory_service)
    purchase: PurchaseActive = cast(PurchaseActive, container.aggregate)
    escrow: EscrowAccount = container.dependencies[EscrowAccount][0]
    store_items: list[StoreItem] = container.dependencies[StoreItem]
    
    purchase_summary = purchase_return_service.payment_cancel(
        purchase, 
        escrow
    )
    
    with pytest.raises(DomainException):
        purchase_summary = purchase_return_service.payment_cancel(
            purchase, 
            escrow
        )
    
    assert purchase.is_finalized()
    assert escrow.is_finalized()
    assert purchase_summary.reason == PurchaseSummaryReason.PAYMENT_CANCELLED
    for item in store_items:
        assert item.amount == 10


def test_purchase_paid_cancel_payment(purchase_return_service_factory: Callable[[InventoryService], PurchaseReturnService],
                                 purchase_active_filled_container_factory: Callable[[], AggregateContainer]) -> None:
    container = purchase_active_filled_container_factory()
    inventory_service = InventoryService(container.dependencies[StoreItem])
    purchase_return_service = purchase_return_service_factory(inventory_service)
    purchase: PurchaseActive = cast(PurchaseActive, container.aggregate)
    escrow: EscrowAccount = container.dependencies[EscrowAccount][0]
    store_items: list[StoreItem] = container.dependencies[StoreItem]
    escrow.mark_as_paid()
    
    with pytest.raises(DomainException):
        purchase_summary = purchase_return_service.payment_cancel(
            purchase, 
            escrow
        )
    
    assert purchase.is_active()
    assert escrow.is_paid()


def test_purchase_unclaim(purchase_return_service_factory: Callable[[InventoryService], PurchaseReturnService],
                                 purchase_active_filled_container_factory: Callable[[], AggregateContainer]) -> None:
    container = purchase_active_filled_container_factory()
    inventory_service = InventoryService(container.dependencies[StoreItem])
    purchase_return_service = purchase_return_service_factory(inventory_service)
    purchase: PurchaseActive = cast(PurchaseActive, container.aggregate)
    escrow: EscrowAccount = container.dependencies[EscrowAccount][0]
    store_items: list[StoreItem] = container.dependencies[StoreItem]
    escrow.mark_as_paid()
    purchase_summary = purchase_return_service.unclaim(
        purchase, 
        escrow
    )
    
    with pytest.raises(DomainException):
        purchase_summary = purchase_return_service.unclaim(
            purchase, 
            escrow
        )
    
    assert purchase.is_finalized()
    assert escrow.is_refunding()
    assert purchase_summary.reason == PurchaseSummaryReason.NOT_CLAIMED
    for item in store_items:
        assert item.amount == 10


def test_purchase_pending_unclaim(purchase_return_service_factory: Callable[[InventoryService], PurchaseReturnService],
                                 purchase_active_filled_container_factory: Callable[[], AggregateContainer]) -> None:
    container = purchase_active_filled_container_factory()
    inventory_service = InventoryService(container.dependencies[StoreItem])
    purchase_return_service = purchase_return_service_factory(inventory_service)
    purchase: PurchaseActive = cast(PurchaseActive, container.aggregate)
    escrow: EscrowAccount = container.dependencies[EscrowAccount][0]
    store_items: list[StoreItem] = container.dependencies[StoreItem]
    
    with pytest.raises(DomainException):
        purchase_summary = purchase_return_service.unclaim(
            purchase, 
            escrow
        )
    
    assert purchase.is_active()
    assert escrow.is_pending()