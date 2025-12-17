from taskiq import AsyncBroker

from shop_project.infrastructure.background_tasks.broker import make_broker
from shop_project.infrastructure.background_tasks.task_handler_registrator import (
    register_background_tasks,
)
from shop_project.infrastructure.dependency_injection.factories import (
    container_taskiq_worker_factory,
)


def broker() -> AsyncBroker:
    broker = make_broker()
    container = container_taskiq_worker_factory(broker)
    register_background_tasks(broker)
    broker.state["di_container"] = container
    return broker
