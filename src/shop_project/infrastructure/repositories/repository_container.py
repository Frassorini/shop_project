from typing import Any, Literal, Mapping, Type, TypeVar, cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import Session

from shop_project.application.dto.base_dto import BaseDTO

from shop_project.shared.entity_id import EntityId

from shop_project.domain.interfaces.persistable_entity import PersistableEntity
from shop_project.domain.entities.customer import Customer
from shop_project.domain.entities.purchase_draft import PurchaseDraft
from shop_project.domain.entities.purchase_active import PurchaseActive
from shop_project.domain.entities.purchase_summary import PurchaseSummary
from shop_project.domain.entities.escrow_account import EscrowAccount
from shop_project.domain.entities.product import Product
from shop_project.domain.entities.shipment import Shipment
from shop_project.domain.entities.shipment_summary import ShipmentSummary

from shop_project.infrastructure.repositories.base_repository import BaseRepository

from shop_project.infrastructure.query.base_query import BaseQuery
from shop_project.infrastructure.query.composed_query import ComposedQuery
from shop_project.infrastructure.query.custom_query import CustomQuery



class RepositoryContainer:
    def __init__(self, repositories: dict[Type[PersistableEntity], BaseRepository[PersistableEntity]]) -> None:
        self.repositories: dict[Type[PersistableEntity], BaseRepository[PersistableEntity]] = repositories
    
    async def load_scalars(self, query: BaseQuery) -> Any:
        return await self.repositories[query.model_type].load_scalars(query)
    
    async def load(self, query: BaseQuery) -> list[PersistableEntity]:
        return await self.repositories[query.model_type].load(query)
    
    async def save(self, resource_changes_snapshot: dict[Type[PersistableEntity], dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[BaseDTO]]]) -> None:
        for entity_type, difference in resource_changes_snapshot.items():
            await self.repositories[entity_type].save(difference)
    
    def get_unique_id(self, model_type: type[PersistableEntity]) -> EntityId:
        raise NotImplementedError


def repository_container_factory(session: AsyncSession, repositories: Mapping[Type[PersistableEntity], Type[BaseRepository[Any]]]) -> RepositoryContainer:
    return RepositoryContainer({model_type: repository(session) for model_type, repository in repositories.items()})

























