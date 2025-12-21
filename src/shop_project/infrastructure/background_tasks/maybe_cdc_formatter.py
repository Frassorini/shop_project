import json
from typing import Any

from pydantic import ValidationError
from taskiq.abc.formatter import TaskiqFormatter
from taskiq.compat import model_dump_json, model_validate_json
from taskiq.message import BrokerMessage, TaskiqMessage


class MaybeCDCFormatter(TaskiqFormatter):
    """Default taskiq formatter."""

    def dumps(self, message: TaskiqMessage) -> BrokerMessage:
        """
        Dumps taskiq message to some broker message format.

        :param message: message to send.
        :return: Dumped message.
        """
        return BrokerMessage(
            task_id=message.task_id,
            task_name=message.task_name,
            message=model_dump_json(message).encode(),
            labels=message.labels,
        )

    def loads(self, message: bytes) -> TaskiqMessage:
        """
        Loads json from message.

        :param message: broker's message.
        :return: parsed taskiq message.
        """
        try:
            return model_validate_json(TaskiqMessage, message)
        except ValidationError:
            pass
        try:
            decoded: dict[str, Any] = json.loads(message)
            return TaskiqMessage(
                task_id=decoded["data"]["entity_id"],
                task_name=decoded["data"]["handler"],
                args=[],
                kwargs={"task_id": decoded["data"]["entity_id"]},
                labels={},
            )
        except Exception:
            raise
