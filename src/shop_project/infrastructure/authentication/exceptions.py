class AuthException(Exception):
    pass


class AuthTypeMismatchException(AuthException):
    pass


class AuthSessionExpiredException(AuthException):
    pass
