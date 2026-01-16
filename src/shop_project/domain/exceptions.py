from abc import ABC

from shop_project.domain.base_exceptions.error_code import ErrorCode
from shop_project.domain.base_exceptions.user_visible_exception import (
    UserVisibleException,
)


class DomainException(UserVisibleException, ABC):
    pass


class DomainInvalidStateError(DomainException):
    code = ErrorCode.INVALID_STATE


class DomainValidationError(DomainException):
    code = ErrorCode.VALIDATION_ERROR


class DomainNotFoundError(DomainException):
    code = ErrorCode.NOT_FOUND


class DomainConflictError(DomainException):
    code = ErrorCode.CONFLICT
