# shop_project/domain/factories.py
from dependency_injector.wiring import inject, Provide

from shop_project.domain.services.checkout_service import CheckoutService
from shop_project.domain.services.purchase_activation_service import PurchaseActivationService
from shop_project.domain.services.purchase_reservation_service import PurchaseReservationService
from shop_project.domain.services.purchase_return_service import PurchaseReturnService
from shop_project.domain.services.purchase_summary_service import PurchaseSummaryService
from shop_project.domain.services.purchase_claim_service import PurchaseClaimService
from shop_project.domain.services.shipment_activation_service import ShipmentActivationService
from shop_project.domain.services.shipment_receive_service import ShipmentReceiveService
from shop_project.domain.services.shipment_cancel_service import ShipmentCancelService
from shop_project.domain.services.shipment_summary_service import ShipmentSummaryService


def checkout_service_factory() -> CheckoutService:
    return CheckoutService()

def purchase_reservation_service_factory() -> PurchaseReservationService:
    return PurchaseReservationService()

def purchase_summary_service_factory() -> PurchaseSummaryService:
    return PurchaseSummaryService()

@inject
def purchase_activation_service_factory(
    reservation_service: PurchaseReservationService = Provide["purchase_reservation_service"],
    checkout_service: CheckoutService = Provide["checkout_service"],
) -> PurchaseActivationService:
    return PurchaseActivationService(reservation_service, checkout_service)

@inject
def purchase_return_service_factory(
    purchase_summary_service: PurchaseSummaryService = Provide["purchase_summary_service"],
) -> PurchaseReturnService:
    return PurchaseReturnService(purchase_summary_service)

@inject
def purchase_claim_service_factory(
    purchase_summary_service: PurchaseSummaryService = Provide["purchase_summary_service"],
) -> PurchaseClaimService:
    return PurchaseClaimService(purchase_summary_service)


def shipment_summary_service_factory() -> ShipmentSummaryService:
    return ShipmentSummaryService()

def shipment_activation_service_factory(
) -> ShipmentActivationService:
    return ShipmentActivationService()

@inject
def shipment_receive_service_factory(
    shipment_summary_service: ShipmentSummaryService = Provide["shipment_summary_service"],
) -> ShipmentReceiveService:
    return ShipmentReceiveService(shipment_summary_service)

@inject
def shipment_cancel_service_factory(
    shipment_summary_service: ShipmentSummaryService = Provide["shipment_summary_service"],
) -> ShipmentCancelService:
    return ShipmentCancelService(shipment_summary_service)
