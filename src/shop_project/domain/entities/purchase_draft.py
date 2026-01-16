from dataclasses import dataclass
from enum import Enum
from typing import Self
from uuid import UUID

from shop_project.domain.exceptions import (
    DomainConflictError,
    DomainInvalidStateError,
    DomainNotFoundError,
    DomainValidationError,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.stock_item import StockItem
from shop_project.shared.base_state_machine import BaseStateMachine


@dataclass(frozen=True)
class PurchaseDraftItem(StockItem):
    product_id: UUID
    amount: int

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise DomainValidationError("Amount must be > 0")


class PurchaseDraftState(Enum):
    ACTIVE = "ACTIVE"
    FINALIZED = "FINALIZED"


class PurchaseDraftStateMachine(BaseStateMachine[PurchaseDraftState]):
    _transitions = {
        PurchaseDraftState.ACTIVE: [PurchaseDraftState.FINALIZED],
    }


class PurchaseDraft(PersistableEntity):
    entity_id: UUID
    customer_id: UUID
    _items_map: dict[UUID, PurchaseDraftItem]
    _state_machine: PurchaseDraftStateMachine

    def __init__(self, entity_id: UUID, customer_id: UUID) -> None:
        super().__init__()
        self.entity_id: UUID = entity_id
        self.customer_id: UUID = customer_id
        self._items_map: dict[UUID, PurchaseDraftItem] = {}
        self._state_machine = PurchaseDraftStateMachine(PurchaseDraftState.ACTIVE)

    @classmethod
    def load(
        cls,
        entity_id: UUID,
        customer_id: UUID,
        items: list[PurchaseDraftItem],
        state: PurchaseDraftState,
    ) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj.customer_id = customer_id
        obj._items_map = {item.product_id: item for item in items}
        obj._state_machine = PurchaseDraftStateMachine(state)

        return obj

    @property
    def state(self) -> PurchaseDraftState:
        return self._state_machine.state

    def _validate_item(self, product_id: UUID) -> None:
        if product_id in self._items_map:
            raise DomainConflictError("Item already added")

        if len(self._items_map) >= 40:
            raise DomainValidationError("Too many items")

    def add_item(self, product_id: UUID, amount: int) -> None:
        if self.state == PurchaseDraftState.FINALIZED:
            raise DomainInvalidStateError("Cannot add item to finalized draft")

        if product_id in self._items_map:
            new_amount = self._items_map[product_id].amount + amount
            self._items_map.pop(product_id)

            self._validate_item(product_id)

            self._items_map[product_id] = PurchaseDraftItem(
                product_id=product_id,
                amount=new_amount,
            )

            return

        self._validate_item(product_id)

        self._items_map[product_id] = PurchaseDraftItem(
            product_id=product_id,
            amount=amount,
        )

    def remove_item(self, product_id: UUID) -> None:
        if self.state == PurchaseDraftState.FINALIZED:
            raise DomainInvalidStateError("Cannot remove item from finalized draft")

        if product_id not in self._items_map:
            raise DomainNotFoundError("Item not found")

        self._items_map.pop(product_id)

    def get_item(self, product_id: UUID) -> PurchaseDraftItem:
        try:
            return self._items_map[product_id]
        except KeyError:
            raise DomainNotFoundError("Item not found")

    def __contains__(self, product_id: UUID) -> bool:
        return product_id in self._items_map

    @property
    def items(self) -> list[PurchaseDraftItem]:
        return sorted(self._items_map.values(), key=lambda item: item.product_id)

    def finalize(self) -> None:
        self._state_machine.try_transition_to(PurchaseDraftState.FINALIZED)

    def is_finalized(self) -> bool:
        return self.state == PurchaseDraftState.FINALIZED

    def is_active(self) -> bool:
        return self.state == PurchaseDraftState.ACTIVE
