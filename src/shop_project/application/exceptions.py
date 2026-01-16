from shop_project.domain.base_exceptions.error_code import ErrorCode
from shop_project.domain.base_exceptions.user_visible_exception import (
    UserVisibleException,
)


class ApplicationException(UserVisibleException):
    pass


class ApplicationAlreadyExistsError(ApplicationException):
    code = ErrorCode.CONFLICT


class ApplicationConflictError(ApplicationException):
    code = ErrorCode.CONFLICT


class ApplicationForbiddenError(ApplicationException):
    code = ErrorCode.FORBIDDEN


class ApplicationNotFoundError(ApplicationException):
    code = ErrorCode.NOT_FOUND
