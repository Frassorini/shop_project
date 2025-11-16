from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Generator, Self

from urllib.parse import quote
from shop_project.infrastructure.message_broker.task_container import TaskContainer
from shop_project.infrastructure.env_loader import get_env

if TYPE_CHECKING:
    from taskiq.abc.broker import AsyncBroker


class BrokerContainer:
    """
    This class is used to not have to make if TYPE_CHECKING imports in other modules
    """
    def __init__(self, broker: "AsyncBroker") -> None:
        self.broker = broker
        self.task_container = TaskContainer(broker)
