from typing import (
    Callable,
    Coroutine,
    Type,
)

import pytest
from dishka.async_container import AsyncContainer

from shop_project.application.customer.queries.catalogue_customer_read_service import (
    CatalogueCustomerReadService,
)
from shop_project.domain.entities.product import Product
from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from tests.helpers import AggregateContainer


@pytest.mark.asyncio
async def test_catalogue_customer_service(
    prepare_container: Callable[
        [Type[PersistableEntity]], Coroutine[None, None, AggregateContainer]
    ],
    async_container: AsyncContainer,
) -> None:

    model_type: Type[PersistableEntity] = Product
    domain_container: AggregateContainer = await prepare_container(model_type)
    catalogue_service = await async_container.get(CatalogueCustomerReadService)
    product: Product = (
        domain_container.aggregate
    )  # pyright: ignore[reportAssignmentType]

    product_schemas = await catalogue_service.get_products_by_ids(
        ids=[product.entity_id]
    )

    assert len(product_schemas) == 1
    assert product_schemas[0].entity_id == product.entity_id
