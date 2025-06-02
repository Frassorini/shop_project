from typing import Callable
from domain.entity_id import EntityId
from domain.store_item import StoreItem
from domain.customer import Customer
from domain.cart import Cart
from domain.cart_item import CartItem


def test_item_in_cart(unique_id_factory: Callable[[], EntityId], potatoes_store_item_1: Callable[[], StoreItem]) -> None:
    cart = Cart(unique_id_factory())
    item = potatoes_store_item_1()
    cart_item = CartItem(unique_id_factory(), item, 1)
    
    cart.items.append(cart_item)
    
    assert cart_item in cart.items


def test_sub_item_from_cart(unique_id_factory: Callable[[], EntityId],potatoes_store_item_1: Callable[[], StoreItem]) -> None:
    item = potatoes_store_item_1()
    cart_item = CartItem(unique_id_factory(), item, 1)
    same_cart_item = CartItem(unique_id_factory(), item, 1)
    cart = Cart(unique_id_factory(), items=[cart_item])
    
    cart -= cart_item
    
    assert cart_item not in cart


def test_cart_add_cart_item(unique_id_factory: Callable[[], EntityId],potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes_cart = CartItem(unique_id_factory(), store_item=potatoes_store_item_10(), amount=5)
    cart = Cart(unique_id_factory(),)
    
    cart += potatoes_cart
    
    assert potatoes_cart in cart


def test_cutomer_cart(unique_id_factory: Callable[[], EntityId],customer_andrew: Callable[[], Customer], potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    customer: Customer = customer_andrew()
    potatoes_cart = CartItem(unique_id_factory(), store_item=potatoes_store_item_10(), amount=5)
    
    customer.cart += potatoes_cart
    
    assert potatoes_cart in customer.cart


def test_cart_price(unique_id_factory: Callable[[], EntityId],potatoes_store_item_10: Callable[[], StoreItem], sausages_store_item_10: Callable[[], StoreItem]) -> None:
    potatoes_cart = CartItem(unique_id_factory(), store_item=potatoes_store_item_10(), amount=5)
    sausages_cart = CartItem(unique_id_factory(), store_item=sausages_store_item_10(), amount=5)
    cart = Cart(unique_id_factory(), [potatoes_cart, sausages_cart])
    
    assert cart.price == 1*5 + 1*5