from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import AsyncGenerator, Callable
from urllib.parse import quote

from taskiq.abc.broker import AsyncBroker
from taskiq.brokers.inmemory_broker import InMemoryBroker
from taskiq_aio_pika.broker import AioPikaBroker

from shop_project.application.background.exceptions import RetryException
from shop_project.infrastructure.background_tasks.maybe_cdc_formatter import (
    MaybeCDCFormatter,
)
from shop_project.infrastructure.background_tasks.on_smart_retry_fail_middleware import (
    OnSmartRetryFailMiddleware,
)
from shop_project.infrastructure.background_tasks.on_task_fail_actions import (
    log_message_taskiq,
)
from shop_project.infrastructure.background_tasks.task_handler_registrator import (
    register_background_tasks,
)
from shop_project.infrastructure.env_loader import get_env


def make_broker() -> "AioPikaBroker":
    from taskiq_aio_pika.broker import AioPikaBroker

    user = get_env("RABBITMQ_DEFAULT_USER")
    password = get_env("RABBITMQ_DEFAULT_PASS")
    host = get_env("RABBITMQ_HOST")
    port = get_env("RABBITMQ_PORT")
    vhost = quote(get_env("RABBITMQ_VHOST"), safe="")
    url = f"amqp://{user}:{password}@{host}:{port}/{vhost}"

    broker = (
        AioPikaBroker(broker_url=url, exchange_name="tasks")
        .with_middlewares(
            OnSmartRetryFailMiddleware(
                default_delay=5,
                use_jitter=True,
                use_delay_exponent=True,
                max_delay_exponent=60,
                default_retry_count=3,
                default_retry_label=True,
                types_of_exceptions=[RetryException],
                on_out_of_retries_callback=log_message_taskiq,
            )
        )
        .with_formatter(MaybeCDCFormatter())
    )

    return broker


def make_broker_inmem() -> "InMemoryBroker":
    from taskiq.brokers.inmemory_broker import InMemoryBroker

    broker = InMemoryBroker(await_inplace=True)

    return broker


def producer_broker_context_factory(
    broker_factory: Callable[[], "AsyncBroker"],
) -> Callable[[], AbstractAsyncContextManager["AsyncBroker"]]:
    @asynccontextmanager
    async def _inner() -> AsyncGenerator["AsyncBroker", None]:
        broker = broker_factory()
        register_background_tasks(broker)
        try:
            await broker.startup()
            yield broker
        finally:
            await broker.shutdown()

    return _inner
