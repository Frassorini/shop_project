from collections import defaultdict
from typing import Sequence
from uuid import UUID

from shop_project.application.shared.interfaces.interface_resource_container import (
    IResourceContainer,
)
from shop_project.domain.entities.escrow_account import (
    EscrowAccount,
)
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_summary import PurchaseSummary


def get_escrow_purchase_active_map(
    resources: IResourceContainer,
) -> list[tuple[EscrowAccount, PurchaseActive]]:
    escrow_accounts: Sequence[EscrowAccount] = resources.get_all(EscrowAccount)
    purchases: Sequence[PurchaseActive] = resources.get_all(PurchaseActive)

    escrow_purchase_map: dict[UUID, list[EscrowAccount | PurchaseActive | None]] = (
        defaultdict(lambda: [None, None])
    )

    for escrow_account in escrow_accounts:
        escrow_purchase_map[escrow_account.entity_id][0] = escrow_account

    for purchase in purchases:
        escrow_purchase_map[purchase.entity_id][1] = purchase

    filtered: list[tuple[EscrowAccount, PurchaseActive]] = []

    for entity_id, (escrow_account, purchase_active) in escrow_purchase_map.items():
        if not isinstance(escrow_account, EscrowAccount):
            assert purchase_active is PurchaseActive
            print(f"PurchaseActive {purchase_active.entity_id} has no EscrowAccount")
            continue
        if not isinstance(purchase_active, PurchaseActive):
            print(f"EscrowAccount {escrow_account.entity_id} has no PurchaseActive")
            continue

        filtered.append((escrow_account, purchase_active))

    return filtered


def get_escrow_purchase_summary_map(
    resources: IResourceContainer,
) -> list[tuple[EscrowAccount, PurchaseSummary]]:
    escrow_accounts: Sequence[EscrowAccount] = resources.get_all(EscrowAccount)
    purchases: Sequence[PurchaseSummary] = resources.get_all(PurchaseSummary)

    escrow_purchase_map: dict[UUID, list[EscrowAccount | PurchaseSummary | None]] = (
        defaultdict(lambda: [None, None])
    )

    for escrow_account in escrow_accounts:
        escrow_purchase_map[escrow_account.entity_id][0] = escrow_account

    for purchase in purchases:
        escrow_purchase_map[purchase.entity_id][1] = purchase

    filtered: list[tuple[EscrowAccount, PurchaseSummary]] = []

    for entity_id, (escrow_account, purchase_active) in escrow_purchase_map.items():
        if not isinstance(escrow_account, EscrowAccount):
            assert purchase_active is PurchaseSummary
            print(f"PurchaseSummary {purchase_active.entity_id} has no EscrowAccount")
            continue
        if not isinstance(purchase_active, PurchaseSummary):
            print(f"EscrowAccount {escrow_account.entity_id} has no PurchaseSummary")
            continue

        filtered.append((escrow_account, purchase_active))

    return filtered
