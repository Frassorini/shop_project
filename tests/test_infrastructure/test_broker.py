import asyncio
import pytest

from shop_project.infrastructure.message_broker.broker import make_broker_inmem
from shop_project.infrastructure.message_broker.broker_container import BrokerContainer
from shop_project.infrastructure.message_broker.task_container import TaskContainer


async def echo(message: str) -> str:
    return message


@pytest.mark.asyncio
async def test_broker(request: pytest.FixtureRequest, test_broker_container: BrokerContainer) -> None:
    if request.config.getoption("--real-broker"):
        pytest.skip("Test requires in-memory broker")

    task_container = test_broker_container.task_container
    
    echo_task = task_container.get_task(echo)

    task1 = await echo_task.kiq(message="test_message")
    
    res = await task1.wait_result()

    assert res.return_value == "test_message"
