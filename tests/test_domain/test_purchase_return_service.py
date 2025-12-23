from typing import Callable, cast

import pytest
from dishka.container import Container

from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_summary import PurchaseSummaryReason
from shop_project.domain.exceptions import DomainException
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.services.purchase_return_service import PurchaseReturnService
from tests.helpers import AggregateContainer


def test_purchase_cancel_payment(
    purchase_active_filled_container_factory: Callable[[], AggregateContainer],
    domain_container: Container,
) -> None:
    purchase_return_service = domain_container.get(PurchaseReturnService)

    container = purchase_active_filled_container_factory()
    product_inventory = ProductInventory(container.dependencies[Product])
    purchase: PurchaseActive = cast(PurchaseActive, container.aggregate)
    escrow: EscrowAccount = container.dependencies[EscrowAccount][0]
    products: list[Product] = container.dependencies[Product]

    escrow.cancel_payment()

    purchase_summary = purchase_return_service.handle_cancelled_payment(
        product_inventory=product_inventory,
        purchase_active=purchase,
        escrow_account=escrow,
    )

    with pytest.raises(DomainException):
        purchase_summary = purchase_return_service.handle_cancelled_payment(
            product_inventory=product_inventory,
            purchase_active=purchase,
            escrow_account=escrow,
        )

    assert purchase.is_finalized()
    assert escrow.is_finalized()
    assert purchase_summary.reason == PurchaseSummaryReason.PAYMENT_CANCELLED
    for item in products:
        assert item.amount == 10


def test_purchase_paid_cancel_payment(
    purchase_active_filled_container_factory: Callable[[], AggregateContainer],
    domain_container: Container,
) -> None:
    purchase_return_service = domain_container.get(PurchaseReturnService)

    container = purchase_active_filled_container_factory()
    product_inventory = ProductInventory(container.dependencies[Product])
    purchase: PurchaseActive = cast(PurchaseActive, container.aggregate)
    escrow: EscrowAccount = container.dependencies[EscrowAccount][0]
    products: list[Product] = container.dependencies[Product]
    escrow.mark_as_paid()

    with pytest.raises(DomainException):
        purchase_summary = purchase_return_service.handle_cancelled_payment(
            product_inventory=product_inventory,
            purchase_active=purchase,
            escrow_account=escrow,
        )

    assert purchase.is_active()
    assert escrow.is_paid()


def test_purchase_unclaim(
    purchase_active_filled_container_factory: Callable[[], AggregateContainer],
    domain_container: Container,
) -> None:
    purchase_return_service = domain_container.get(PurchaseReturnService)

    container = purchase_active_filled_container_factory()
    product_inventory = ProductInventory(container.dependencies[Product])
    purchase: PurchaseActive = cast(PurchaseActive, container.aggregate)
    escrow: EscrowAccount = container.dependencies[EscrowAccount][0]
    products: list[Product] = container.dependencies[Product]

    escrow.mark_as_paid()

    purchase_summary = purchase_return_service.unclaim(
        product_inventory=product_inventory,
        purchase_active=purchase,
        escrow_account=escrow,
    )

    with pytest.raises(DomainException):
        purchase_summary = purchase_return_service.unclaim(
            product_inventory=product_inventory,
            purchase_active=purchase,
            escrow_account=escrow,
        )

    assert purchase.is_finalized()
    assert escrow.is_refunding()
    assert purchase_summary.reason == PurchaseSummaryReason.NOT_CLAIMED
    for item in products:
        assert item.amount == 10


def test_purchase_pending_unclaim(
    purchase_active_filled_container_factory: Callable[[], AggregateContainer],
    domain_container: Container,
) -> None:
    purchase_return_service = domain_container.get(PurchaseReturnService)

    container = purchase_active_filled_container_factory()
    product_inventory = ProductInventory(container.dependencies[Product])
    purchase: PurchaseActive = cast(PurchaseActive, container.aggregate)
    escrow: EscrowAccount = container.dependencies[EscrowAccount][0]
    products: list[Product] = container.dependencies[Product]

    with pytest.raises(DomainException):
        purchase_summary = purchase_return_service.unclaim(
            product_inventory=product_inventory,
            purchase_active=purchase,
            escrow_account=escrow,
        )

    assert purchase.is_active()
    assert escrow.is_pending()
