from dataclasses import dataclass
from enum import Enum
from typing import Self
from uuid import UUID

from shop_project.domain.interfaces.persistable_entity import PersistableEntity


@dataclass(frozen=True)
class PurchaseSummaryItem:
    product_id: UUID
    amount: int


class PurchaseSummaryReason(Enum):
    PAYMENT_CANCELLED = "PAYMENT_CANCELLED"
    CLAIMED = "CLAIMED"
    NOT_CLAIMED = "NOT_CLAIMED"


class PurchaseSummary(PersistableEntity):
    entity_id: UUID
    customer_id: UUID
    escrow_account_id: UUID
    reason: PurchaseSummaryReason
    _items: dict[UUID, PurchaseSummaryItem]

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
    def load(
        cls,
        entity_id: UUID,
        customer_id: UUID,
        escrow_account_id: UUID,
        reason: PurchaseSummaryReason,
        items: list[PurchaseSummaryItem],
    ) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj.customer_id = customer_id
        obj.escrow_account_id = escrow_account_id
        obj.reason = reason
        obj._items = {item.product_id: item for item in items}

        return obj

    def get_item(self, product_id: UUID) -> PurchaseSummaryItem:
        return self._items[product_id]

    @property
    def items(self) -> list[PurchaseSummaryItem]:
        return list(self._items.values())

    def get_items(self) -> list[PurchaseSummaryItem]:
        return list(self._items.values())
