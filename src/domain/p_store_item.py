from typing import Protocol, override


class PStoreItem(Protocol):
    name: str
    store: str
    price: float
    
    @property
    def amount(self) -> float:
        ...
    
    @amount.setter
    def amount(self, value: float) -> None:
        ...
    
    @property
    def id_(self) -> int | None:
        ...
    
    @id_.setter
    def id_(self, value: int) -> None:
        ...
    
    @override
    def __eq__(self, value: object, /) -> bool:
        ...