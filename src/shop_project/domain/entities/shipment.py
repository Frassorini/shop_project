from dataclasses import dataclass
from enum import Enum
from typing import Any, Self
from uuid import UUID

from shop_project.domain.exceptions import DomainException
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.stock_item import StockItem
from shop_project.shared.base_state_machine import BaseStateMachine
from shop_project.shared.p_snapshotable import PSnapshotable


@dataclass(frozen=True)
class ShipmentItem(StockItem, PSnapshotable):
    product_id: UUID
    amount: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_id": self.product_id,
            "amount": self.amount,
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        return cls(snapshot["product_id"], snapshot["amount"])

    def _validate(self) -> None:
        if self.amount <= 0:
            raise DomainException("Amount must be > 0")


class ShipmentState(Enum):
    ACTIVE = "ACTIVE"
    FINALIZED = "FINALIZED"


class ShipmentStateMachine(BaseStateMachine[ShipmentState]):
    _transitions: dict[ShipmentState, list[ShipmentState]] = {
        ShipmentState.ACTIVE: [ShipmentState.FINALIZED],
        ShipmentState.FINALIZED: [],
    }


class Shipment(PersistableEntity):
    def __init__(self, entity_id: UUID, items: list[ShipmentItem]) -> None:
        self.entity_id: UUID = entity_id
        self._state_machine: ShipmentStateMachine = ShipmentStateMachine(
            ShipmentState.ACTIVE
        )

        self._items: dict[UUID, ShipmentItem] = {}

        for item in items:
            self._validate_item(item)
            self._items[item.product_id] = item

    @property
    def state(self) -> ShipmentState:
        return self._state_machine.state

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "state": self.state.value,
            "items": [item.to_dict() for item in self._items.values()],
        }

    @classmethod
    def from_dict(cls, snapshot: dict[str, Any]) -> Self:
        obj = cls(
            snapshot["entity_id"],
            [ShipmentItem.from_dict(item) for item in snapshot["items"]],
        )
        obj._state_machine = ShipmentStateMachine(ShipmentState(snapshot["state"]))
        return obj

    def _validate_item(self, item: ShipmentItem) -> None:
        if item.product_id in self._items:
            raise DomainException("Item already added")

    def get_item(self, product_id: UUID) -> ShipmentItem:
        return self._items[product_id]

    def get_items(self) -> list[ShipmentItem]:
        return list(self._items.values())

    def finalize(self) -> None:
        self._state_machine.try_transition_to(ShipmentState.FINALIZED)

    def is_finalized(self) -> bool:
        return self.state == ShipmentState.FINALIZED

    def is_active(self) -> bool:
        return self.state == ShipmentState.ACTIVE
