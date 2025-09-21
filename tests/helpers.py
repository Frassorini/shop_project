from dataclasses import dataclass, field
from typing import Generic, Type, TypeVar
from shop_project.domain.base_aggregate import BaseAggregate

@dataclass
class AggregateContainer():
    aggregate: BaseAggregate
    dependencies: dict[Type[BaseAggregate], list[BaseAggregate]] = field(default_factory=dict)