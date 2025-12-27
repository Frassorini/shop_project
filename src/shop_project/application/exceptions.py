class ApplicationException(Exception):
    pass


class AlreadyExistsException(ApplicationException):
    pass


class ForbiddenException(ApplicationException):
    pass


class NotFoundException(ApplicationException):
    pass


class TaskException(Exception):
    pass


class RetryException(TaskException):
    pass


class AlreadyDoneException(TaskException):
    pass
