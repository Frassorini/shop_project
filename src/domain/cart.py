from collections.abc import Iterator
from typing import Self
from domain.cart_item import CartItem
from domain.domain_object import DomainObject


class Cart(DomainObject):
    def __init__(self, items: list[CartItem]|None=None) -> None:
        super().__init__()
        self.items: list[CartItem] = [] if items is None else items
    
    @property
    def price(self) -> float:
        return sum([item.price for item in self.items])
    
    def __add__(self, other: CartItem) -> Self:
        self.items.append(other)
        return self
    
    def __sub__(self, other: CartItem) -> Self:
        self.items.remove(other)
        return self
    
    def __contains__(self, item: CartItem) -> bool:
        return item in self.items

    def __iter__(self) -> Iterator[CartItem]:
        return self.items.__iter__()