from typing import Callable
from domain.customer_order_item import CustomerOrderItem
from domain.p_store_item import PStoreItem
from domain.store_item import StoreItem
from domain.customer import Customer
from domain.cart import Cart
from domain.cart_item import CartItem
from domain.customer_order import CustomerOrder, CustomerOrderState
from domain.exceptions import DomainException, NegativeAmountException, StateException
import pytest


def test_order_reserve_fixed_price(customer_andrew: Customer, 
                                potatoes_store_item_10: StoreItem, 
                                sausages_store_item_10: StoreItem) -> None:
    order = CustomerOrder(customer=customer_andrew, store='Moscow')
    order += CustomerOrderItem(store_item=potatoes_store_item_10, amount=5)
    order += CustomerOrderItem(store_item=sausages_store_item_10, amount=5)

    order.reserve()
    potatoes_store_item_10.price = 10
    
    assert order.price == 5 * 1 + 5 * 1


def test_order_reserve_price_is_sum_of_items_price(customer_order_potatoes_10_factory: Callable[[], CustomerOrder]) -> None: 
    order = customer_order_potatoes_10_factory()

    order.reserve()
    
    assert order.price == sum([item.price for item in order.items])


def test_order_cancel(customer_andrew: Customer, 
                       potatoes_store_item_10: StoreItem) -> None:
    customer_andrew.cart += CartItem(potatoes_store_item_10, 5)
    order = CustomerOrder(customer_andrew, store='Moscow')
    for item in customer_andrew.cart.items:
        order += CustomerOrderItem(store_item=item.store_item, amount=item.amount)
    order.reserve()
    
    order.cancel()
    
    assert potatoes_store_item_10.amount == 10
    assert order.state == CustomerOrderState.CANCELLED


def test_order_receive_wrong_receiver(customer_order_potatoes_10_factory: Callable[[], CustomerOrder], customer_bob: Customer) -> None: 
    order = customer_order_potatoes_10_factory()
    order.reserve()
    order.pay()
    
    with pytest.raises(DomainException):
        order.receive(receiver=customer_bob)


def test_raise_empty_order(customer_andrew: Customer) -> None:
    order = CustomerOrder(customer_andrew, store='Moscow')
    for item in customer_andrew.cart.items:
        order += CustomerOrderItem(store_item=item.store_item, amount=item.amount)
    
    with pytest.raises(DomainException):
        order.reserve()


def test_transitions_receive(customer_order_potatoes_10_factory: Callable[[], CustomerOrder]) -> None: 
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


def test_transitions_pay(customer_order_potatoes_10_factory: Callable[[], CustomerOrder]) -> None: 
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


def test_transitions_reserve(customer_order_potatoes_10_factory: Callable[[], CustomerOrder]) -> None: 
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


def test_invalid_transitions_cancel(customer_order_potatoes_10_factory: Callable[[], CustomerOrder]) -> None:
    order = customer_order_potatoes_10_factory()
    with pytest.raises(StateException):
        order.cancel()
        
    order.reserve()
    order.pay()
    order.receive(receiver=order.customer)
    
    with pytest.raises(StateException):
        order.cancel()


def test_add_to_order(potatoes_store_item_10: PStoreItem, customer_andrew: Customer) -> None:
    potatoes = CustomerOrderItem(store_item=potatoes_store_item_10, amount=10)
    order = CustomerOrder(customer=customer_andrew, store='Moscow')
    order += potatoes
    
    assert len(order.items) == 1


def test_sub_from_order(potatoes_store_item_10: PStoreItem, customer_andrew: Customer) -> None:
    potatoes = CustomerOrderItem(store_item=potatoes_store_item_10, amount=10)
    order = CustomerOrder(customer=customer_andrew, store='Moscow')
    order += potatoes
    
    order -= potatoes
    
    assert len(order.items) == 0


def test_add_item_has_correct_store(potatoes_store_item_10_petersburg: PStoreItem, customer_andrew: Customer) -> None:
    potatoes = CustomerOrderItem(store_item=potatoes_store_item_10_petersburg, amount=10)
    order = CustomerOrder(customer_andrew, store='Moscow')
    
    with pytest.raises(DomainException):
        order += potatoes


def test_add_item_is_not_reserved(potatoes_store_item_10: PStoreItem, customer_andrew: Customer) -> None:
    potatoes = CustomerOrderItem(store_item=potatoes_store_item_10, amount=10)
    potatoes.reserve()
    customer_order = CustomerOrder(customer_andrew, store='Moscow')
    
    with pytest.raises(DomainException):
        customer_order += potatoes
        

def test_sub_item_is_not_reserved(potatoes_store_item_10: PStoreItem, customer_andrew: Customer) -> None:
    potatoes = CustomerOrderItem(store_item=potatoes_store_item_10, amount=10)
    customer_order = CustomerOrder(customer_andrew, store='Moscow')
    customer_order += potatoes
    potatoes.reserve()
    
    with pytest.raises(DomainException):
        customer_order -= potatoes


def test_price_changes_before_reserve(potatoes_store_item_10: PStoreItem, customer_andrew: Customer) -> None:
    potatoes = CustomerOrderItem(store_item=potatoes_store_item_10, amount=10)
    customer_order = CustomerOrder(customer_andrew, store='Moscow')
    customer_order += potatoes
    potatoes.store_item.price = 100
    
    assert customer_order.price == 100 * 10
    