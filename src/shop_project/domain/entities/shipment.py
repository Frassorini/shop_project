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
from shop_project.shared.base_state_machine import BaseStateMachine


@dataclass(frozen=True)
class ShipmentItem(StockItem):
    product_id: UUID
    amount: int

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise DomainValidationError("Amount must be > 0")


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
    def load(
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
            raise DomainConflictError("Item already added")

    def get_item(self, product_id: UUID) -> ShipmentItem:
        try:
            return self._items[product_id]
        except KeyError:
            raise DomainNotFoundError("Item not found")

    @property
    def items(self) -> list[ShipmentItem]:
        return sorted(self._items.values(), key=lambda item: item.product_id)

    def finalize(self) -> None:
        self._state_machine.try_transition_to(ShipmentState.FINALIZED)

    def is_finalized(self) -> bool:
        return self.state == ShipmentState.FINALIZED

    def is_active(self) -> bool:
        return self.state == ShipmentState.ACTIVE
