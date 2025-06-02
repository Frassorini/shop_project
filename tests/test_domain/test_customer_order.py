from typing import Callable
from domain.customer_order_item import CustomerOrderItem
from domain.entity_id import EntityId
from domain.store_item import StoreItem
from domain.customer import Customer
from domain.cart import Cart
from domain.cart_item import CartItem
from domain.customer_order import CustomerOrder, CustomerOrderState
from domain.exceptions import DomainException, NegativeAmountException, StateException
import pytest


def test_order_reserve_fixed_price(
    unique_id_factory: Callable[[], EntityId],
    customer_andrew: Callable[[], Customer],
    potatoes_store_item_10: Callable[[], StoreItem],
    sausages_store_item_10: Callable[[], StoreItem]
) -> None:
    customer = customer_andrew()
    potatoes = potatoes_store_item_10()
    sausages = sausages_store_item_10()
    
    order = CustomerOrder(unique_id_factory(), customer=customer, store='Moscow')
    order += CustomerOrderItem(unique_id_factory(), store_item=potatoes, amount=5)
    order += CustomerOrderItem(unique_id_factory(), store_item=sausages, amount=5)

    order.reserve()
    potatoes.price = 10
    
    assert order.price == 5 * 1 + 5 * 1


def test_order_reserve_price_is_sum_of_items_price(
    customer_order_potatoes_10_factory: Callable[[], CustomerOrder]
) -> None: 
    order = customer_order_potatoes_10_factory()
    order.reserve()
    assert order.price == sum([item.price for item in order.items])


def test_order_cancel(
    unique_id_factory: Callable[[], EntityId],
    customer_andrew: Callable[[], Customer],
    potatoes_store_item_10: Callable[[], StoreItem]
) -> None:
    customer = customer_andrew()
    potatoes = potatoes_store_item_10()
    
    customer.cart += CartItem(unique_id_factory(), store_item=potatoes, amount=5)
    order = CustomerOrder(unique_id_factory(), customer=customer, store='Moscow')
    for item in customer.cart.items:
        order += CustomerOrderItem(unique_id_factory(), store_item=item.store_item, amount=item.amount)
    order.reserve()
    
    order.cancel()
    
    assert potatoes.amount == 10
    assert order.state == CustomerOrderState.CANCELLED


def test_order_receive_wrong_receiver(
    customer_order_potatoes_10_factory: Callable[[], CustomerOrder],
    customer_bob: Callable[[], Customer]
) -> None: 
    order = customer_order_potatoes_10_factory()
    order.reserve()
    order.pay()
    
    with pytest.raises(DomainException):
        order.receive(receiver=customer_bob())


def test_raise_empty_order(
    unique_id_factory: Callable[[], EntityId],
    customer_andrew: Callable[[], Customer]
) -> None:
    customer = customer_andrew()
    order = CustomerOrder(unique_id_factory(), customer=customer, store='Moscow')
    
    with pytest.raises(DomainException):
        order.reserve()


def test_transitions_receive(
    customer_order_potatoes_10_factory: Callable[[], CustomerOrder]
) -> None: 
    order = customer_order_potatoes_10_factory()
    
    with pytest.raises(StateException):
        order.receive(receiver=order.customer)
    
    order.reserve()
    with pytest.raises(StateException):
        order.receive(receiver=order.customer)
    
    order.pay()
    order.receive(receiver=order.customer)
    assert order.state == CustomerOrderState.RECEIVED
    with pytest.raises(StateException):
        order.receive(receiver=order.customer)


def test_transitions_pay(
    customer_order_potatoes_10_factory: Callable[[], CustomerOrder]
) -> None: 
    order = customer_order_potatoes_10_factory()
    
    with pytest.raises(StateException):
        order.pay()
    
    order.reserve()
    order.pay()
    assert order.state == CustomerOrderState.PAID
    with pytest.raises(StateException):
        order.pay()
    
    order.receive(receiver=order.customer)
    with pytest.raises(StateException):
        order.pay()


def test_transitions_reserve(
    customer_order_potatoes_10_factory: Callable[[], CustomerOrder]
) -> None: 
    order = customer_order_potatoes_10_factory()
    
    order.reserve()
    assert order.state == CustomerOrderState.RESERVED
    with pytest.raises(StateException):
        order.reserve()
    
    order.pay()
    with pytest.raises(StateException):
        order.reserve()
    
    order.receive(receiver=order.customer)
    with pytest.raises(StateException):
        order.reserve()


def test_invalid_transitions_cancel(
    customer_order_potatoes_10_factory: Callable[[], CustomerOrder]
) -> None:
    order = customer_order_potatoes_10_factory()
    with pytest.raises(StateException):
        order.cancel()
        
    order.reserve()
    order.pay()
    order.receive(receiver=order.customer)
    
    with pytest.raises(StateException):
        order.cancel()


def test_add_to_order(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem],
    customer_andrew: Callable[[], Customer]
) -> None:
    potatoes = potatoes_store_item_10()
    customer = customer_andrew()
    potatoes_item = CustomerOrderItem(unique_id_factory(), store_item=potatoes, amount=10)
    order = CustomerOrder(unique_id_factory(), customer=customer, store='Moscow')
    order += potatoes_item
    
    assert len(order.items) == 1


def test_sub_from_order(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem],
    customer_andrew: Callable[[], Customer]
) -> None:
    potatoes = potatoes_store_item_10()
    customer = customer_andrew()
    potatoes_item = CustomerOrderItem(unique_id_factory(), store_item=potatoes, amount=10)
    order = CustomerOrder(unique_id_factory(), customer=customer, store='Moscow')
    order += potatoes_item
    
    order -= potatoes_item
    
    assert len(order.items) == 0


def test_add_item_has_correct_store(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[..., StoreItem],
    customer_andrew: Callable[[], Customer]
) -> None:
    potatoes = potatoes_store_item_10(store='Petersburg')
    customer = customer_andrew()
    potatoes_item = CustomerOrderItem(unique_id_factory(), store_item=potatoes, amount=10)
    order = CustomerOrder(unique_id_factory(), customer=customer, store='Moscow')
    
    with pytest.raises(DomainException):
        order += potatoes_item


def test_add_item_is_not_reserved(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem],
    customer_andrew: Callable[[], Customer]
) -> None:
    potatoes = potatoes_store_item_10()
    customer = customer_andrew()
    potatoes_item = CustomerOrderItem(unique_id_factory(), store_item=potatoes, amount=10)
    potatoes_item.reserve()
    customer_order = CustomerOrder(unique_id_factory(), customer=customer, store='Moscow')
    
    with pytest.raises(DomainException):
        customer_order += potatoes_item
        

def test_sub_item_is_not_reserved(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem],
    customer_andrew: Callable[[], Customer]
) -> None:
    potatoes = potatoes_store_item_10()
    customer = customer_andrew()
    potatoes_item = CustomerOrderItem(unique_id_factory(), store_item=potatoes, amount=10)
    customer_order = CustomerOrder(unique_id_factory(), customer=customer, store='Moscow')
    customer_order += potatoes_item
    potatoes_item.reserve()
    
    with pytest.raises(DomainException):
        customer_order -= potatoes_item


def test_price_changes_before_reserve(
    unique_id_factory: Callable[[], EntityId],
    potatoes_store_item_10: Callable[[], StoreItem],
    customer_andrew: Callable[[], Customer]
) -> None:
    potatoes = potatoes_store_item_10()
    customer = customer_andrew()
    potatoes_item = CustomerOrderItem(unique_id_factory(), store_item=potatoes, amount=10)
    customer_order = CustomerOrder(unique_id_factory(), customer=customer, store='Moscow')
    customer_order += potatoes_item
    potatoes.price = 100
    
    assert customer_order.price == 100 * 10