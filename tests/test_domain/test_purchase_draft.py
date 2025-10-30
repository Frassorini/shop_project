from typing import Callable

import pytest
from shop_project.domain.exceptions import DomainException
from shop_project.domain.product import Product
from shop_project.domain.purchase_draft import PurchaseDraft, PurchaseDraftItem



def test_add_item(purchase_draft_factory: Callable[[], PurchaseDraft],
                  potatoes_product_10: Callable[[], Product]) -> None:
    cart = purchase_draft_factory()
    product: Product = potatoes_product_10()
    
    cart.add_item(product_id=product.entity_id, amount=2)


def test_add_negative_amount(purchase_draft_factory: Callable[[], PurchaseDraft],
                  potatoes_product_10: Callable[[], Product]) -> None:
    cart = purchase_draft_factory()
    product: Product = potatoes_product_10()
    
    with pytest.raises(DomainException):
        cart.add_item(product_id=product.entity_id, amount=-2)


def test_get_item(purchase_draft_factory: Callable[[], PurchaseDraft],
                  potatoes_product_10: Callable[[], Product]) -> None:
    product: Product = potatoes_product_10()
    cart = purchase_draft_factory()
    
    cart.add_item(product_id=product.entity_id, amount=2)
    
    cart_item: PurchaseDraftItem = cart.get_item(product.entity_id)
    
    assert cart_item.amount == 2


def test_cannot_add_duplicate_item(purchase_draft_factory: Callable[[], PurchaseDraft], 
                                   potatoes_product_10: Callable[[], Product]) -> None:
    product: Product = potatoes_product_10()
    cart = purchase_draft_factory()
    
    cart.add_item(product_id=product.entity_id, amount=2)
    with pytest.raises(DomainException):
        cart.add_item(product_id=product.entity_id, amount=3)
    

def test_snapshot(purchase_draft_factory: Callable[[], PurchaseDraft], 
                  potatoes_product_10: Callable[[], Product]) -> None:
    product: Product = potatoes_product_10()
    cart: PurchaseDraft = purchase_draft_factory()
    
    cart.add_item(product_id=product.entity_id, amount=2)
    
    snapshot = cart.to_dict()
    
    assert snapshot['items'][0] == {'product_id': product.entity_id.value, 'amount': 2}


def test_from_snapshot(purchase_draft_factory: Callable[[], PurchaseDraft], 
                       potatoes_product_10: Callable[[], Product]) -> None:
    product: Product = potatoes_product_10()
    cart: PurchaseDraft = purchase_draft_factory()
    
    cart.add_item(product_id=product.entity_id, amount=2)
    
    snapshot = cart.to_dict()
    
    cart_from_snapshot: PurchaseDraft = PurchaseDraft.from_dict(snapshot)
    
    assert cart_from_snapshot.get_items() == cart.get_items()
    