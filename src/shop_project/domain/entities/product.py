from decimal import Decimal
from typing import Self
from uuid import UUID

from shop_project.domain.exceptions import NegativeAmountException
from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class Product(PersistableEntity):
    entity_id: UUID
    name: str
    _amount: int
    price: Decimal

    def __init__(self, entity_id: UUID, name: str, amount: int, price: Decimal) -> None:
        super().__init__()
        self.entity_id: UUID = entity_id
        self.name: str = name
        if amount < 0:
            raise NegativeAmountException("amount field must be >= 0")
        self._amount: int = amount
        self.price: Decimal = price

    @classmethod
    def _load(cls, entity_id: UUID, name: str, amount: int, price: Decimal) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj.name = name
        obj._amount = amount
        obj.price = price

        return obj

    def reserve(self, amount: int) -> None:
        self.amount -= amount

    def restock(self, amount: int) -> None:
        self.amount += amount

    @property
    def amount(self) -> int:
        return self._amount

    @amount.setter
    def amount(self, value: int) -> None:
        if value < 0:
            raise NegativeAmountException("amount field must be >= 0")
        self._amount = value
