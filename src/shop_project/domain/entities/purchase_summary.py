from dataclasses import dataclass
from enum import Enum
from typing import Any, Self
from uuid import UUID

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.shared.p_snapshotable import PSnapshotable


@dataclass(frozen=True)
class PurchaseSummaryItem(PSnapshotable):
    product_id: UUID
    amount: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_id": self.product_id,
            "amount": self.amount,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(
            product_id=snapshot["product_id"],
            amount=snapshot["amount"],
        )


class PurchaseSummaryReason(Enum):
    PAYMENT_CANCELLED = "PAYMENT_CANCELLED"
    CLAIMED = "CLAIMED"
    NOT_CLAIMED = "NOT_CLAIMED"


class PurchaseSummary(PersistableEntity):
    def __init__(
        self,
        entity_id: UUID,
        customer_id: UUID,
        escrow_account_id: UUID,
        reason: PurchaseSummaryReason,
        items: list[PurchaseSummaryItem],
    ) -> None:
        self.entity_id: UUID = entity_id

        self.customer_id: UUID = customer_id
        self.escrow_account_id: UUID = escrow_account_id
        self.reason: PurchaseSummaryReason = reason

        self._items: dict[UUID, PurchaseSummaryItem] = {}

        for item in items:
            self._items[item.product_id] = item

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls(
            snapshot["entity_id"],
            snapshot["customer_id"],
            snapshot["escrow_account_id"],
            PurchaseSummaryReason(snapshot["reason"]),
            [PurchaseSummaryItem.from_dict(item) for item in snapshot["items"]],
        )

        return obj

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "customer_id": self.customer_id,
            "escrow_account_id": self.escrow_account_id,
            "reason": self.reason.value,
            "items": [item.to_dict() for item in self._items.values()],
        }

    def get_item(self, product_id: UUID) -> PurchaseSummaryItem:
        return self._items[product_id]

    def get_items(self) -> list[PurchaseSummaryItem]:
        return list(self._items.values())
