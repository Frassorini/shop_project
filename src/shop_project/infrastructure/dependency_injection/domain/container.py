from lagom import Container

# --- Доменные сервисы ---
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


class DomainContainer(Container):
    """
    Контейнер для всех доменных сервисов.
    Использует type-based auto-wiring Lagom.
    """

    def __init__(self):
        super().__init__()

        # --- Базовые сервисы ---
        # Эти сервисы не зависят от других сервисов
        self[CheckoutService] = CheckoutService
        self[PurchaseReservationService] = PurchaseReservationService
        self[PurchaseSummaryService] = PurchaseSummaryService
        self[ShipmentSummaryService] = ShipmentSummaryService

        # --- Сервисы с зависимостями ---
        # Lagom сам создаст все зависимости через type hints __init__
        self[PurchaseActivationService] = PurchaseActivationService
        self[PurchaseReturnService] = PurchaseReturnService
        self[PurchaseClaimService] = PurchaseClaimService
        self[ShipmentActivationService] = ShipmentActivationService
        self[ShipmentReceiveService] = ShipmentReceiveService
        self[ShipmentCancelService] = ShipmentCancelService
