from dataclasses import dataclass
from enum import Enum
from typing import Any, Self
from uuid import UUID

from shop_project.domain.exceptions import DomainException
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.stock_item import StockItem
from shop_project.shared.base_state_machine import BaseStateMachine


@dataclass(frozen=True)
class ShipmentItem(StockItem):
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
    entity_id: UUID
    _items: dict[UUID, ShipmentItem]
    _state_machine: ShipmentStateMachine

    def __init__(self, entity_id: UUID, items: list[ShipmentItem]) -> None:
        self.entity_id: UUID = entity_id
        self._state_machine: ShipmentStateMachine = ShipmentStateMachine(
            ShipmentState.ACTIVE
        )

        self._items: dict[UUID, ShipmentItem] = {}

        for item in items:
            self._validate_item(item)
            self._items[item.product_id] = item

    @classmethod
    def _load(
        cls, entity_id: UUID, items: list[ShipmentItem], state: ShipmentState
    ) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj._items = {item.product_id: item for item in items}
        obj._state_machine = ShipmentStateMachine(state)

        return obj

    @property
    def state(self) -> ShipmentState:
        return self._state_machine.state

    def _validate_item(self, item: ShipmentItem) -> None:
        if item.product_id in self._items:
            raise DomainException("Item already added")

    def get_item(self, product_id: UUID) -> ShipmentItem:
        return self._items[product_id]

    @property
    def items(self) -> list[ShipmentItem]:
        return list(self._items.values())

    def get_items(self) -> list[ShipmentItem]:
        return list(self._items.values())

    def finalize(self) -> None:
        self._state_machine.try_transition_to(ShipmentState.FINALIZED)

    def is_finalized(self) -> bool:
        return self.state == ShipmentState.FINALIZED

    def is_active(self) -> bool:
        return self.state == ShipmentState.ACTIVE
