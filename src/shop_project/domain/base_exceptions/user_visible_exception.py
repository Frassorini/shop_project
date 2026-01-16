from abc import ABC

from shop_project.domain.base_exceptions.error_code import ErrorCode


class UserVisibleException(Exception, ABC):
    code: ErrorCode
