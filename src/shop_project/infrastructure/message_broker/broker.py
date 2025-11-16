from typing import TYPE_CHECKING, AsyncGenerator, Callable
import asyncio
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from urllib.parse import quote

from shop_project.infrastructure.env_loader import get_env
from shop_project.infrastructure.message_broker.broker_container import BrokerContainer
from src.shop_project.infrastructure.message_broker.task_container import TaskContainer

if TYPE_CHECKING: # taskiq takes insanely long time to initialize itself (>300ms just for import without usage)
    from taskiq.brokers.inmemory_broker import InMemoryBroker
    from taskiq_aio_pika.broker import AioPikaBroker
    from taskiq.abc.broker import AsyncBroker


def make_broker() -> "AioPikaBroker":
    from taskiq_aio_pika.broker import AioPikaBroker
    user = get_env("RABBITMQ_DEFAULT_USER")
    password = get_env("RABBITMQ_DEFAULT_PASS")
    host = get_env("RABBITMQ_HOST")
    port = get_env("RABBITMQ_PORT")
    vhost = quote(get_env("RABBITMQ_VHOST"), safe='')
    url = f"amqp://{user}:{password}@{host}:{port}/{vhost}"
    
    broker = AioPikaBroker(broker_url=url)

    container = TaskContainer(broker) # Register tasks

    return broker


def make_broker_inmem() -> "InMemoryBroker":
    from taskiq.brokers.inmemory_broker import InMemoryBroker
    broker =  InMemoryBroker()

    container = TaskContainer(broker) # Register tasks

    return broker


def producer_broker_context_factory(broker_factory: Callable[[], "AsyncBroker"]) -> Callable[[], AbstractAsyncContextManager[BrokerContainer]]:
    @asynccontextmanager
    async def _inner() -> AsyncGenerator[BrokerContainer, None]:
        broker = broker_factory()
        try:
            await broker.startup()
            yield BrokerContainer(broker)
        finally:
            await broker.shutdown()
    
    return _inner


def consumer_broker_context_factory(broker_factory: Callable[[], "AsyncBroker"]) -> Callable[[], AbstractAsyncContextManager[BrokerContainer]]:
    @asynccontextmanager
    async def _inner() -> AsyncGenerator[BrokerContainer, None]:
        broker = broker_factory()
        yield BrokerContainer(broker)
    
    return _inner

