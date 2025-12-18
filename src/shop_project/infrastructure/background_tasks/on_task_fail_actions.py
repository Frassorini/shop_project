from taskiq import TaskiqMessage


async def log_message_taskiq(
    taskiq_message: TaskiqMessage, exception: BaseException
) -> None:
    print(taskiq_message, exception)
