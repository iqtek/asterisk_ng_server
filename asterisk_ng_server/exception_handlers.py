from fastapi import Request
from fastapi.responses import JSONResponse

from asterisk_ng_server.exceptions import InvalidMethodParamsException
from asterisk_ng_server.exceptions import LongPoolTimeout
from asterisk_ng_server.exceptions import UnknownMethodException


__all__ = [

    "unknown_method_exception_handler",
    "invalid_method_params_exception_handler",
    "long_pool_handler",
]


async def invalid_method_params_exception_handler(request: Request, exc: InvalidMethodParamsException):
    return JSONResponse(
        content={
            "headers":
                {
                    "status_code": "410",
                    "detail": f"Invalid method parameters method: {exc.method}; params: {exc.params}"
                }
        },
    )


async def unknown_method_exception_handler(request: Request, exc: UnknownMethodException):
    return JSONResponse(
        content={"headers": {"status_code": "404", "detail": f"Unknown method: {exc.method}"}},
    )


async def long_pool_handler(request: Request, exc: LongPoolTimeout):
    return JSONResponse(
        content={"headers": {"status_code": "408", "detail": f"Long pool timeout."}},
    )
