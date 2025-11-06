# shop_project/containers/di_container.py
from typing import Iterable
from dishka import make_container, Provider, provide, Scope # type: ignore

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


class DomainProvider(Provider):
    scope = Scope.APP  # Можно передавать через __init__ при необходимости

    # Простые фабрики
    checkout_service = provide(CheckoutService)
    purchase_reservation_service = provide(PurchaseReservationService)
    purchase_summary_service = provide(PurchaseSummaryService)
    shipment_summary_service = provide(ShipmentSummaryService)
    shipment_activation_service = provide(ShipmentActivationService)

    # Фабрики с зависимостями
    @provide
    def purchase_activation_service(
        self,
        reservation_service: PurchaseReservationService,
        checkout_service: CheckoutService,
    ) -> Iterable[PurchaseActivationService]:
        yield PurchaseActivationService(reservation_service, checkout_service)

    @provide
    def purchase_return_service(
        self,
        purchase_summary_service: PurchaseSummaryService,
    ) -> Iterable[PurchaseReturnService]:
        yield PurchaseReturnService(purchase_summary_service)

    @provide
    def purchase_claim_service(
        self,
        purchase_summary_service: PurchaseSummaryService,
    ) -> Iterable[PurchaseClaimService]:
        yield PurchaseClaimService(purchase_summary_service)

    @provide
    def shipment_receive_service(
        self,
        shipment_summary_service: ShipmentSummaryService,
    ) -> Iterable[ShipmentReceiveService]:
        yield ShipmentReceiveService(shipment_summary_service)

    @provide
    def shipment_cancel_service(
        self,
        shipment_summary_service: ShipmentSummaryService,
    ) -> Iterable[ShipmentCancelService]:
        yield ShipmentCancelService(shipment_summary_service)

