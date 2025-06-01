from domain.cart import Cart
from domain.domain_object import DomainObject
from domain.exceptions import DomainException


class Customer(DomainObject):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name: str = name
        self.cart: Cart = Cart()
