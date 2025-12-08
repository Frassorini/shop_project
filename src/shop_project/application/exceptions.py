class ApplicationException(Exception):
    pass


class AlreadyExistsException(ApplicationException):
    pass


class ForbiddenException(ApplicationException):
    pass
