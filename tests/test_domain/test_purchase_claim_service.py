from typing import Callable, cast
import pytest

from dishka.container import Container

from shop_project.domain.exceptions import DomainException
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.entities.purchase_summary import PurchaseSummaryReason
from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from shop_project.domain.helpers.product_inventory import ProductInventory
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.escrow_account import EscrowAccount
from tests.helpers import AggregateContainer


def test_purchase_claim(purchase_active_filled_container_factory: Callable[[], AggregateContainer],
                        domain_container: Container,) -> None:
    purchase_claim_service = domain_container.get(PurchaseClaimService)

    container = purchase_active_filled_container_factory()
    product_inventory = ProductInventory(container.dependencies[Product])
    purchase: PurchaseActive = cast(PurchaseActive, container.aggregate)
    escrow: EscrowAccount = container.dependencies[EscrowAccount][0]
    products: list[Product] = container.dependencies[Product]
    escrow.mark_as_paid()
    purchase_summary = purchase_claim_service.claim(
        purchase, 
        escrow
    )
    
    with pytest.raises(DomainException):
        purchase_summary = purchase_claim_service.claim(
            purchase, 
            escrow
        )
    
    assert purchase.is_finalized()
    assert escrow.is_finalized()
    assert purchase_summary.reason == PurchaseSummaryReason.CLAIMED


def test_purchase_pending_claim(purchase_active_filled_container_factory: Callable[[], AggregateContainer],
                                domain_container: Container,) -> None:
    purchase_claim_service = domain_container.get(PurchaseClaimService)

    container = purchase_active_filled_container_factory()
    product_inventory = ProductInventory(container.dependencies[Product])
    purchase: PurchaseActive = cast(PurchaseActive, container.aggregate)
    escrow: EscrowAccount = container.dependencies[EscrowAccount][0]
    products: list[Product] = container.dependencies[Product]
    
    with pytest.raises(DomainException):
        purchase_summary = purchase_claim_service.claim(
            purchase, 
            escrow
        )
    
    assert purchase.is_active()
    assert escrow.is_pending()
