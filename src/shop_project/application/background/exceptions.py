class TaskException(Exception):
    pass


class RetryException(TaskException):
    pass


class AlreadyDoneException(TaskException):
    pass
