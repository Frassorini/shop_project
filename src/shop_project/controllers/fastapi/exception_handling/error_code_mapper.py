from http import HTTPStatus

from shop_project.domain.base_exceptions.error_code import ErrorCode

_ERROR_CODE_TO_HTTP_STATUS: dict[ErrorCode, HTTPStatus] = {
    ErrorCode.INVALID_STATE: HTTPStatus.CONFLICT,
    ErrorCode.VALIDATION_ERROR: HTTPStatus.CONFLICT,
    ErrorCode.NOT_FOUND: HTTPStatus.NOT_FOUND,
    ErrorCode.CONFLICT: HTTPStatus.CONFLICT,
    ErrorCode.UNAUTHORIZED: HTTPStatus.UNAUTHORIZED,
    ErrorCode.FORBIDDEN: HTTPStatus.FORBIDDEN,
}


def _validate_error_code_mapping() -> None:
    missing_codes = set(ErrorCode) - set(_ERROR_CODE_TO_HTTP_STATUS.keys())

    if missing_codes:
        missing = ", ".join(code.name for code in missing_codes)
        raise RuntimeError(
            f"ErrorCode mapping is incomplete. Missing mappings for: {missing}"
        )


_validate_error_code_mapping()


def map_error_code_to_http_status(code: ErrorCode) -> int:
    return _ERROR_CODE_TO_HTTP_STATUS[code].value
