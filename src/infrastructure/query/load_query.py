from enum import Enum
from typing import Type

from domain.p_aggregate import PAggregate
from infrastructure.query.p_attribute_provider import PAttributeProvider

# Под капотом в репозиториях все равно должен использоваться advisory lock
# в дополнение к классическим блокировкам для приоритизации запросов на запись
class QueryLock(Enum):
    FOR_SHARE = 'FOR SHARE'
    FOR_UPDATE = 'FOR UPDATE'
    NO_LOCK = 'NO LOCK'


class LoadQuery():
    def __init__(
        self,
        model_type: type,
        attribute_provider: PAttributeProvider,
        lock: QueryLock,
    ) -> None:
        self.model_type: Type[PAggregate] = model_type
        self.attribute_provider: PAttributeProvider = attribute_provider
        self.lock: QueryLock = lock
        self.result: list[PAggregate] = []
        self.is_loaded: bool = False
