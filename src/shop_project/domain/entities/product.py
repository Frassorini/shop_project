from decimal import Decimal
from typing import Self
from uuid import UUID

from shop_project.domain.exceptions import DomainValidationError
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
        self._amount: int = amount
        self.price: Decimal = price

        self._validate()

    @classmethod
    def load(cls, entity_id: UUID, name: str, amount: int, price: Decimal) -> Self:
        obj = cls.__new__(cls)

        obj.entity_id = entity_id
        obj.name = name
        obj._amount = amount
        obj.price = price

        obj._validate()

        return obj

    def _validate(self) -> None:
        if self.amount < 0:
            raise DomainValidationError("amount field must be >= 0")

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
            raise DomainValidationError("amount field must be >= 0")
        self._amount = value
