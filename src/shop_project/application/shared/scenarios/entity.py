from typing import Sequence, Type, TypeVar
from uuid import UUID

from shop_project.application.exceptions import ForbiddenException, NotFoundException
from shop_project.application.shared.interfaces.interface_resource_container import (
    IResourceContainer,
)
from shop_project.domain.interfaces.persistable_entity import PersistableEntity

T = TypeVar("T", bound=PersistableEntity)


def get_one_or_raise_not_found(
    resources: IResourceContainer, entity_type: Type[T], entity_id: UUID
) -> T:
    maybe_entity = resources.get_by_id_or_none(entity_type, entity_id)
    if not maybe_entity:
        raise NotFoundException
    return maybe_entity


def get_all_or_raise_not_found(
    resources: IResourceContainer, entity_type: Type[T]
) -> Sequence[T]:
    maybe_entities = resources.get_all(entity_type)
    if not maybe_entities:
        raise NotFoundException
    return maybe_entities


def get_one_or_raise_forbidden(
    resources: IResourceContainer, entity_type: Type[T], entity_id: UUID
) -> T:
    maybe_entity = resources.get_by_id_or_none(entity_type, entity_id)
    if not maybe_entity:
        raise ForbiddenException
    return maybe_entity
