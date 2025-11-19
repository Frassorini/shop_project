from typing import Callable

from shop_project.application.dto.mapper import to_domain, to_dto
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_draft import PurchaseDraft


def test_to_dto(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
) -> None:
    purchase_draft = purchase_draft_factory()
    product: Product = potatoes_product_10()
    purchase_draft.add_item(product_id=product.entity_id, amount=2)

    dto = to_dto(purchase_draft)

    assert dto.entity_id == purchase_draft.entity_id.value
    assert dto.state == purchase_draft.state.value
    assert dto.items[0].product_id == purchase_draft.get_items()[0].product_id.value


def test_to_domain(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
) -> None:
    purchase_draft = purchase_draft_factory()
    product: Product = potatoes_product_10()
    purchase_draft.add_item(product_id=product.entity_id, amount=2)

    dto = to_dto(purchase_draft)
    order_from_dto = to_domain(dto)

    assert order_from_dto.entity_id == purchase_draft.entity_id
    assert order_from_dto.state == purchase_draft.state
    assert order_from_dto.get_items() == purchase_draft.get_items()
