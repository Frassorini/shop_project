from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from shop_project.controllers.fastapi.exception_handling.error_code_mapper import (
    map_error_code_to_http_status,
)
from shop_project.domain.base_exceptions.user_visible_exception import (
    UserVisibleException,
)


async def user_visible_exception_handler(request: Request, exc: Exception) -> Response:
    if not isinstance(exc, UserVisibleException):
        return await internal_exception_handler(request, exc)

    http_code = map_error_code_to_http_status(exc.code)

    return JSONResponse(
        status_code=map_error_code_to_http_status(exc.code),
        content={
            "error": {
                "code": exc.code.value,
                "message": exc.args[0] if len(exc.args) > 0 else "",
            }
        },
    )


async def internal_exception_handler(request: Request, exc: Exception) -> Response:
    print(exc)

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserVisibleException, user_visible_exception_handler)
    app.add_exception_handler(Exception, internal_exception_handler)
