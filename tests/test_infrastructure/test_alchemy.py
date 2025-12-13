from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from shop_project.application.dto.mapper import to_dto
from shop_project.application.dto.purchase_draft_dto import (
    PurchaseDraftDTO,
    PurchaseDraftItemDTO,
)
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.infrastructure.database.core import Database
from shop_project.infrastructure.database.models.purchase_draft import (
    PurchaseDraft as PurchaseDraftORM,
    PurchaseDraftItem as PurchaseDraftItemORM,
)
from shop_project.infrastructure.query.query_builder import QueryBuilder
from shop_project.infrastructure.repositories.implementations.purchase_draft_repository import (
    PurchaseDraftRepository,
)


@pytest.mark.asyncio
async def xtest_alchemy(test_db: Database) -> None:
    async with test_db.session() as session:
        draft_1 = PurchaseDraftORM(
            entity_id=uuid4(), customer_id=uuid4(), state="draft"
        )
        draft_item_1 = PurchaseDraftItemORM(
            parent_id=draft_1.entity_id, product_id=uuid4(), amount=1
        )
        draft_2 = PurchaseDraftORM(
            entity_id=uuid4(), customer_id=uuid4(), state="draft"
        )
        draft_item_2 = PurchaseDraftItemORM(
            parent_id=draft_2.entity_id, product_id=uuid4(), amount=2
        )

        session.add(draft_1)
        session.add(draft_item_1)
        session.add(draft_2)
        session.add(draft_item_2)

        await session.commit()

    async with test_db.session() as session:
        draft_1 = await session.get_one(PurchaseDraftORM, draft_1.entity_id)
        draft_item_1 = await session.get_one(
            PurchaseDraftItemORM, (draft_item_1.parent_id, draft_item_1.product_id)
        )
        draft_2 = await session.get_one(PurchaseDraftORM, draft_2.entity_id)
        draft_item_2 = await session.get_one(
            PurchaseDraftItemORM, (draft_item_2.parent_id, draft_item_2.product_id)
        )

        draft_item_3 = PurchaseDraftItemORM(
            parent_id=draft_1.entity_id, product_id=uuid4(), amount=1
        )
        draft_item_4 = PurchaseDraftItemORM(
            parent_id=draft_2.entity_id, product_id=uuid4(), amount=1
        )
        session.add(draft_item_3)
        session.add(draft_item_4)
        await session.delete(draft_item_1)
        await session.delete(draft_item_2)

        await session.commit()


@pytest.mark.asyncio
async def xtest_alchemy_2(test_db: Database) -> None:
    async with test_db.session() as session:
        draft_1 = PurchaseDraftORM(
            entity_id=uuid4(), customer_id=uuid4(), state="draft"
        )
        draft_item_1 = PurchaseDraftItemORM(
            parent_id=draft_1.entity_id, product_id=uuid4(), amount=1
        )

        session.add(draft_1)
        session.add(draft_item_1)

        await session.commit()

    async with test_db.session() as session:
        draft_1 = await session.get_one(PurchaseDraftORM, draft_1.entity_id)
        draft_item_1 = await session.get_one(
            PurchaseDraftItemORM, (draft_item_1.parent_id, draft_item_1.product_id)
        )

        draft_2 = PurchaseDraftORM(
            entity_id=uuid4(), customer_id=uuid4(), state="draft"
        )
        draft_item_2 = PurchaseDraftItemORM(
            parent_id=draft_2.entity_id, product_id=uuid4(), amount=2
        )
        session.add(draft_2)
        session.add(draft_item_2)

        await session.delete(draft_1)
        await session.delete(draft_item_1)

        await session.commit()


@pytest.mark.asyncio
async def xtest_alchemy_3(test_db: Database) -> None:
    async with test_db.session() as session:
        draft_1 = PurchaseDraftORM(
            entity_id=uuid4(), customer_id=uuid4(), state="draft"
        )
        draft_item_1 = PurchaseDraftItemORM(
            parent_id=draft_1.entity_id, product_id=uuid4(), amount=1
        )

        session.add(draft_1)
        session.add(draft_item_1)

        await session.commit()

    async with test_db.session() as session:
        draft_1 = await session.get_one(PurchaseDraftORM, draft_1.entity_id)

        await session.delete(draft_1)

        with pytest.raises(IntegrityError):
            await session.commit()


@pytest.mark.asyncio
async def xtest_alchemy_4(test_db: Database) -> None:
    async with test_db.session() as session:
        draft_1 = PurchaseDraftORM(
            entity_id=uuid4(), customer_id=uuid4(), state="draft"
        )
        draft_item_1 = PurchaseDraftItemORM(
            parent_id=draft_1.entity_id, product_id=uuid4(), amount=1
        )

        session.add(draft_1)
        session.add(draft_item_1)

        await session.commit()

    async with test_db.session() as session:
        draft_1 = await session.get_one(
            PurchaseDraftORM,
            draft_1.entity_id,
            options=[joinedload(PurchaseDraftORM.items)],
        )
        item = draft_1.items[0]

        item.amount = 3

        await session.commit()

    async with test_db.session() as session:
        draft_1 = await session.get_one(
            PurchaseDraftORM,
            draft_1.entity_id,
            options=[joinedload(PurchaseDraftORM.items)],
        )
        item = draft_1.items[0]

        assert item.amount == 3


@pytest.mark.asyncio
async def xtest_alchemy_5(test_db: Database) -> None:
    async with test_db.session() as session:
        draft_1 = PurchaseDraftORM(
            entity_id=uuid4(), customer_id=uuid4(), state="draft"
        )
        draft_item_1 = PurchaseDraftItemORM(
            parent_id=draft_1.entity_id, product_id=uuid4(), amount=1
        )
        draft_2 = PurchaseDraftORM(
            entity_id=uuid4(), customer_id=uuid4(), state="draft"
        )
        draft_item_2 = PurchaseDraftItemORM(
            parent_id=draft_2.entity_id, product_id=uuid4(), amount=2
        )

        session.add(draft_1)
        session.add(draft_item_1)
        session.add(draft_2)
        session.add(draft_item_2)

        await session.commit()

    async with test_db.session() as session:
        draft_1 = await session.get_one(
            PurchaseDraftORM,
            draft_1.entity_id,
            options=[joinedload(PurchaseDraftORM.items)],
        )
        draft_2 = await session.get_one(
            PurchaseDraftORM,
            draft_2.entity_id,
            options=[joinedload(PurchaseDraftORM.items)],
        )

        item = draft_1.items[0]
        item.parent = draft_2

        with pytest.raises(IntegrityError):
            await session.commit()


@pytest.mark.asyncio
async def xtest_repo(test_db: Database) -> None:
    draft_dto = PurchaseDraftDTO(
        entity_id=uuid4(),
        customer_id=uuid4(),
        state="ACTIVE",
        items=[PurchaseDraftItemDTO(product_id=uuid4(), amount=1)],
    )

    async with test_db.session() as session:
        repo = PurchaseDraftRepository(session)

        await repo.create([draft_dto])

        await session.commit()

    query_plan = (
        QueryBuilder(mutating=True)
        .load(PurchaseDraft)
        .from_id([draft_dto.entity_id])
        .for_update()
    ).build()

    async with test_db.session() as session:
        repo = PurchaseDraftRepository(session)

        loaded = await repo.load(query_plan.queries[0])

        dto_before = loaded[0]

        draft_dto_modified = draft_dto.model_copy(deep=True)
        draft_dto_modified.items[0].amount = 2
        draft_dto_modified.customer_id = uuid4()

        await repo.update([draft_dto_modified])

        await session.commit()

    async with test_db.session() as session:
        repo = PurchaseDraftRepository(session)

        loaded = await repo.load(query_plan.queries[0])

        dto_after = loaded[0]

    print(f"{dto_before.__dict__=}", f"{dto_after.__dict__=}")
    assert dto_before.items[0].amount == 1
    assert dto_after.items[0].amount == 2

    async with test_db.session() as session:
        repo = PurchaseDraftRepository(session)

        loaded = await repo.load(query_plan.queries[0])

        await repo.delete([to_dto(loaded[0])])

        await session.commit()

    async with test_db.session() as session:
        repo = PurchaseDraftRepository(session)

        loaded = await repo.load(query_plan.queries[0])

        assert not loaded
