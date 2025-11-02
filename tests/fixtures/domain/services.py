from typing import Callable
import pytest

from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.customer import Customer
from shop_project.domain.services.checkout_service import CheckoutService
from shop_project.domain.product_inventory import ProductInventory

from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from shop_project.domain.services.purchase_reservation_service import PurchaseReservationService
from shop_project.domain.services.purchase_activation_service import PurchaseActivationService
from shop_project.domain.services.purchase_return_service import PurchaseReturnService
from shop_project.domain.services.purchase_summary_service import PurchaseSummaryService

from shop_project.domain.services.shipment_activation_service import ShipmentActivationService
from shop_project.domain.services.shipment_receive_service import ShipmentReceiveService
from shop_project.domain.services.shipment_cancel_service import ShipmentCancelService
from shop_project.domain.services.shipment_summary_service import ShipmentSummaryService

from shop_project.shared.entity_id import EntityId

from tests.helpers import AggregateContainer


@pytest.fixture
def purchase_activation_service_factory() -> Callable[[], PurchaseActivationService]:
    def factory() -> PurchaseActivationService:
        checkout_service = CheckoutService()
        purchase_reservation_service = PurchaseReservationService()
        
        return PurchaseActivationService(purchase_reservation_service=purchase_reservation_service, 
                                         checkout_service=checkout_service
                                         )
        
    return factory


@pytest.fixture
def purchase_return_service_factory() -> Callable[[], PurchaseReturnService]:
    def factory() -> PurchaseReturnService:
        checkout_service = CheckoutService()
        purchase_summary_service = PurchaseSummaryService()
        
        return PurchaseReturnService(purchase_summary_service)
        
    return factory


@pytest.fixture
def purchase_claim_service_factory() -> Callable[[], PurchaseClaimService]:
    def factory() -> PurchaseClaimService:
        purchase_summary_service = PurchaseSummaryService()
        
        return PurchaseClaimService(purchase_summary_service)
        
    return factory


@pytest.fixture
def shipment_activation_service_factory() -> Callable[[], ShipmentActivationService]:
    def factory() -> ShipmentActivationService:
        return ShipmentActivationService()
        
    return factory


@pytest.fixture
def shipment_receive_service_factory() -> Callable[[], ShipmentReceiveService]:
    def factory() -> ShipmentReceiveService:
        shipment_summary_service = ShipmentSummaryService()
        
        return ShipmentReceiveService(shipment_summary_service)
        
    return factory


@pytest.fixture
def shipment_cancel_service_factory() -> Callable[[], ShipmentCancelService]:
    def factory() -> ShipmentCancelService:
        shipment_summary_service = ShipmentSummaryService()
        
        return ShipmentCancelService(shipment_summary_service=shipment_summary_service)
        
    return factory





























