from typing import Callable

import pytest
from domain.exceptions import DomainException
from domain.services.reservation_service import ReservationService
from domain.store_item.inventory_service import InventoryService
from domain.store_item.model import StoreItem
from domain.customer_order.model import CustomerOrder, CustomerOrderState


def test_(potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    inventory_service = InventoryService([potatoes])

    reservation_service = ReservationService(inventory_service)


def test_reserve_customer_order(customer_order_factory: Callable[[], CustomerOrder],
                                potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    order = customer_order_factory()
    order.add_item(store_item_id=potatoes.entity_id, price=potatoes.price, amount=2, store=potatoes.store)
    inventory_service = InventoryService([potatoes])
    reservation_service = ReservationService(inventory_service)

    reservation_service.reserve_customer_order(order)    

    assert potatoes.amount == 8
    assert order.state == CustomerOrderState.RESERVED


def test_reserve_wrong_customer_order(customer_order_factory: Callable[[], CustomerOrder],
                                potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    order = customer_order_factory()
    order.add_item(store_item_id=potatoes.entity_id, price=potatoes.price, amount=2, store=potatoes.store)
    inventory_service = InventoryService([potatoes])
    reservation_service = ReservationService(inventory_service)
    
    order.reserve()

    with pytest.raises(DomainException):
        reservation_service.reserve_customer_order(order)
        

def test_cancel_customer_order(customer_order_factory: Callable[[], CustomerOrder],
                                potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    order = customer_order_factory()
    order.add_item(store_item_id=potatoes.entity_id, price=potatoes.price, amount=2, store=potatoes.store)
    inventory_service = InventoryService([potatoes])
    reservation_service = ReservationService(inventory_service)
    reservation_service.reserve_customer_order(order)
    
    reservation_service.cancel_customer_order(order)

    assert potatoes.amount == 10


def test_cancel_wrong_customer_order(customer_order_factory: Callable[[], CustomerOrder],
                                potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes = potatoes_store_item_10()
    order = customer_order_factory()
    order.add_item(store_item_id=potatoes.entity_id, price=potatoes.price, amount=2, store=potatoes.store)
    inventory_service = InventoryService([potatoes])
    reservation_service = ReservationService(inventory_service)
    
    with pytest.raises(DomainException):
        reservation_service.cancel_customer_order(order)