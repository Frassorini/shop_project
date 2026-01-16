from dataclasses import dataclass
from enum import Enum
from typing import Self
from uuid import UUID

from shop_project.domain.exceptions import (
    DomainConflictError,
    DomainNotFoundError,
    DomainValidationError,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.stock_item import StockItem


@dataclass(frozen=True)
class ShipmentSummaryItem(StockItem):
    product_id: UUID
    amount: int

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise DomainValidationError("Amount must be > 0")


class ShipmentSummaryReason(Enum):
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class ShipmentSummary(PersistableEntity):
    entity_id: UUID
    reason: ShipmentSummaryReason
    _items: dict[UUID, ShipmentSummaryItem]

    def __init__(
        self,
        entity_id: UUID,
        reason: ShipmentSummaryReason,
        items: list[ShipmentSummaryItem],
    ) -> None:
        self.entity_id: UUID = entity_id
        self.reason = reason

        self._items: dict[UUID, ShipmentSummaryItem] = {}

        for item in items:
            self._validate_item(item)
            self._items[item.product_id] = item

    @classmethod
    def load(
        cls,
        entity_id: UUID,
        reason: ShipmentSummaryReason,
        items: list[ShipmentSummaryItem],
    ) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj.reason = reason
        obj._items = {item.product_id: item for item in items}

        return obj

    def _validate_item(self, item: ShipmentSummaryItem) -> None:
        if item.product_id in self._items:
            raise DomainConflictError("Item already added")

    def get_item(self, product_id: UUID) -> ShipmentSummaryItem:
        try:
            return self._items[product_id]
        except KeyError:
            raise DomainNotFoundError("Item not found")

    @property
    def items(self) -> list[ShipmentSummaryItem]:
        return sorted(self._items.values(), key=lambda item: item.product_id)
