import copy
from decimal import Decimal
from typing import Callable

import pytest

from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.application.dto.mapper import to_dto, to_domain
from shop_project.domain.store_item import StoreItem

def test_to_dto(purchase_draft_factory: Callable[[], PurchaseDraft], potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    purchase_draft = purchase_draft_factory()
    store_item: StoreItem = potatoes_store_item_10()
    purchase_draft.add_item(store_item_id=store_item.entity_id, amount=2)
    
    dto = to_dto(purchase_draft)
    
    assert dto.entity_id == purchase_draft.entity_id.value
    assert dto.state == purchase_draft.state.value
    assert dto.items[0].store_item_id == purchase_draft.get_items()[0].store_item_id.value


def test_to_domain(purchase_draft_factory: Callable[[], PurchaseDraft], potatoes_store_item_10: Callable[[], StoreItem]) -> None:
    purchase_draft = purchase_draft_factory()
    store_item: StoreItem = potatoes_store_item_10()
    purchase_draft.add_item(store_item_id=store_item.entity_id, amount=2)
    
    dto = to_dto(purchase_draft)
    order_from_dto = to_domain(dto)
    
    assert order_from_dto.entity_id == purchase_draft.entity_id
    assert order_from_dto.state == purchase_draft.state
    assert order_from_dto.get_items() == purchase_draft.get_items()