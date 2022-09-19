from fastapi import FastAPI

from asterisk_ng_server.controller import asterisk_ng_controller
from asterisk_ng_server.exception_handlers import invalid_method_params_exception_handler
from asterisk_ng_server.exception_handlers import long_pool_handler
from asterisk_ng_server.exception_handlers import unknown_method_exception_handler
from asterisk_ng_server.exceptions import InvalidMethodParamsException
from asterisk_ng_server.exceptions import LongPoolTimeout
from asterisk_ng_server.exceptions import UnknownMethodException
from asterisk_ng_server.middleware import AuthMiddleware


__all__ = [
    "app",
]


app = FastAPI()


async def startup() -> None:
    app.middleware("http")(AuthMiddleware(secret_key="AsteriskNG"))
    app.add_api_route("/asterisk_ng", asterisk_ng_controller, methods=["POST"])

    app.add_exception_handler(UnknownMethodException, unknown_method_exception_handler)
    app.add_exception_handler(InvalidMethodParamsException, invalid_method_params_exception_handler)
    app.add_exception_handler(LongPoolTimeout, long_pool_handler)


async def shutdown() -> None:
    pass

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)
