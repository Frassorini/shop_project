from dataclasses import dataclass
from enum import Enum
from typing import Self
from uuid import UUID

from shop_project.domain.exceptions import DomainException
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.interfaces.stock_item import StockItem
from shop_project.shared.base_state_machine import BaseStateMachine


@dataclass(frozen=True)
class PurchaseDraftItem(StockItem):
    product_id: UUID
    amount: int


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
    _items: dict[UUID, PurchaseDraftItem]
    _state_machine: PurchaseDraftStateMachine

    def __init__(self, entity_id: UUID, customer_id: UUID) -> None:
        super().__init__()
        self.entity_id: UUID = entity_id
        self.customer_id: UUID = customer_id
        self._items: dict[UUID, PurchaseDraftItem] = {}
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
        obj._items = {item.product_id: item for item in items}
        obj._state_machine = PurchaseDraftStateMachine(state)

        return obj

    @property
    def state(self) -> PurchaseDraftState:
        return self._state_machine.state

    def _validate_item(self, product_id: UUID, amount: int) -> None:
        if product_id in self._items:
            raise DomainException("Item already added")

        if amount <= 0:
            raise DomainException("Amount must be > 0")

    def add_item(self, product_id: UUID, amount: int) -> None:
        if self.state == PurchaseDraftState.FINALIZED:
            raise DomainException("Cannot add item to finalized draft")

        self._validate_item(product_id, amount)

        self._items[product_id] = PurchaseDraftItem(
            product_id=product_id,
            amount=amount,
        )

    def get_item(self, product_id: UUID) -> PurchaseDraftItem:
        return self._items[product_id]

    @property
    def items(self) -> list[PurchaseDraftItem]:
        return list(self._items.values())

    def get_items(self) -> list[PurchaseDraftItem]:
        return list(self._items.values())

    def finalize(self) -> None:
        self._state_machine.try_transition_to(PurchaseDraftState.FINALIZED)

    def is_finalized(self) -> bool:
        return self.state == PurchaseDraftState.FINALIZED

    def is_active(self) -> bool:
        return self.state == PurchaseDraftState.ACTIVE
