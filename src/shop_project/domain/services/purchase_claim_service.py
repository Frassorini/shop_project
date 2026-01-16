from shop_project.domain.entities.employee import Employee
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.exceptions import DomainInvalidStateError
from shop_project.domain.services.purchase_summary_service import PurchaseSummaryService


class PurchaseClaimService:
    def __init__(self, purchase_summary_service: PurchaseSummaryService) -> None:
        self._purchase_summary_service: PurchaseSummaryService = (
            purchase_summary_service
        )

    def claim(
        self,
        employee: Employee,
        purchase_active: PurchaseActive,
        escrow_account: EscrowAccount,
    ) -> PurchaseSummary:

        if purchase_active.is_finalized():
            raise DomainInvalidStateError("Cannot claim finalized purchase")

        if not escrow_account.is_paid():
            raise DomainInvalidStateError(
                "Cannot claim purchase with un-paid escrow account"
            )

        escrow_account.finalize()

        return self._purchase_summary_service.finalize_claim(purchase_active)
