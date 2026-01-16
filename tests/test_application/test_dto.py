from typing import Any, Callable, Self, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel

from shop_project.application.shared.base_dto import BaseDTO, DTODynamicRegistry
from shop_project.application.shared.dto.mapper import to_domain, to_dto
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.interfaces.persistable_entity import PersistableEntity


class MyTestEntity(BaseModel, PersistableEntity):
    entity_id: UUID

    x: int

    @classmethod
    def load(cls, *args: Any, **kwargs: Any) -> Self:
        return cls.model_validate(*args, **kwargs, from_attributes=True)


class MyTestDTO(BaseDTO[MyTestEntity]):
    entity_id: UUID
    x: int


def test_to_dto(
    purchase_draft_factory: Callable[[], PurchaseDraft],
    potatoes_product_10: Callable[[], Product],
) -> None:
    purchase_draft = purchase_draft_factory()
    product: Product = potatoes_product_10()
    purchase_draft.add_item(product_id=product.entity_id, amount=2)

    dto = to_dto(purchase_draft)

    assert dto.entity_id == purchase_draft.entity_id
    assert dto.state == purchase_draft.state.value
    assert dto.items[0].product_id == purchase_draft.items[0].product_id


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
    assert order_from_dto.items == purchase_draft.items


T = TypeVar("T", bound=PersistableEntity)


def test_dto_generic() -> None:

    dto = MyTestDTO(x=1, entity_id=uuid4())
    other_dto = MyTestDTO(x=2, entity_id=uuid4())

    assert MyTestEntity in DTODynamicRegistry.map

    ent = DTODynamicRegistry.get(MyTestEntity).to_domain(dto)
    dto_same = MyTestDTO.to_dto(ent)
