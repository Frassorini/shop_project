from domain.store_item import StoreItem
from domain.customer import Customer
from domain.cart import Cart
from domain.cart_item import CartItem


def test_item_in_cart(potatoes_store_item_1: StoreItem) -> None:
    cart = Cart()
    item = potatoes_store_item_1
    cart_item = CartItem(item, 1)
    
    cart.items.append(cart_item)
    
    assert cart_item in cart.items


def test_sub_item_from_cart(potatoes_store_item_1: StoreItem) -> None:
    item = potatoes_store_item_1
    cart_item = CartItem(item, 1)
    cart_item.id_ = 1
    same_cart_item = CartItem(item, 1)
    same_cart_item.id_ = 1
    cart = Cart(items=[cart_item])
    
    cart -= cart_item
    
    assert cart_item not in cart


def test_cart_add_cart_item(potatoes_store_item_10: StoreItem) -> None:
    potatoes_cart = CartItem(store_item=potatoes_store_item_10, amount=5)
    cart = Cart()
    
    cart += potatoes_cart
    
    assert potatoes_cart in cart


def test_cutomer_cart(customer_andrew: Customer, potatoes_store_item_10: StoreItem) -> None:
    potatoes_cart = CartItem(store_item=potatoes_store_item_10, amount=5)
    
    customer_andrew.cart += potatoes_cart
    
    assert potatoes_cart in customer_andrew.cart


def test_cart_price(potatoes_store_item_10: StoreItem, sausages_store_item_10: StoreItem) -> None:
    potatoes_cart = CartItem(store_item=potatoes_store_item_10, amount=5)
    sausages_cart = CartItem(store_item=sausages_store_item_10, amount=5)
    cart = Cart([potatoes_cart, sausages_cart])
    
    assert cart.price == 1*5 + 1*5