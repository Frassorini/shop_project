from typing import Any, Literal, Mapping, Type, TypeVar, cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import Session

from shop_project.application.dto.base_dto import BaseDTO

from shop_project.shared.entity_id import EntityId

from shop_project.domain.base_aggregate import BaseAggregate
from shop_project.domain.customer import Customer
from shop_project.domain.purchase_draft import PurchaseDraft
from shop_project.domain.purchase_active import PurchaseActive
from shop_project.domain.purchase_summary import PurchaseSummary
from shop_project.domain.escrow_account import EscrowAccount
from shop_project.domain.product import Product
from shop_project.domain.shipment import Shipment
from shop_project.domain.shipment_summary import ShipmentSummary

from shop_project.infrastructure.repositories.base_repository import BaseRepository

from shop_project.infrastructure.query.base_load_query import BaseLoadQuery
from shop_project.infrastructure.query.domain_load_query import DomainLoadQuery
from shop_project.infrastructure.query.prebuilt_load_query import PrebuiltLoadQuery



class RepositoryContainer:
    def __init__(self, repositories: dict[Type[BaseAggregate], BaseRepository[BaseAggregate]]) -> None:
        self.repositories: dict[Type[BaseAggregate], BaseRepository[BaseAggregate]] = repositories
    
    async def load_scalars(self, query: BaseLoadQuery) -> Any:
        return await self.repositories[query.model_type].load_scalars(query)
    
    async def load(self, query: BaseLoadQuery) -> list[BaseAggregate]:
        return await self.repositories[query.model_type].load(query)
    
    async def save(self, resource_changes_snapshot: dict[Type[BaseAggregate], dict[Literal['CREATED', 'UPDATED', 'DELETED'], list[BaseDTO]]]) -> None:
        for entity_type, difference in resource_changes_snapshot.items():
            await self.repositories[entity_type].save(difference)
    
    def get_unique_id(self, model_type: type[BaseAggregate]) -> EntityId:
        raise NotImplementedError


def repository_container_factory(session: AsyncSession, repositories: Mapping[Type[BaseAggregate], Type[BaseRepository[Any]]]) -> RepositoryContainer:
    return RepositoryContainer({model_type: repository(session) for model_type, repository in repositories.items()})

























