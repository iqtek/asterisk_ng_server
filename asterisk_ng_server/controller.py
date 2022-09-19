from typing import Any
from typing import Mapping

from fastapi import Form
from fastapi.responses import JSONResponse

from pydantic import BaseModel
from pydantic import ValidationError

from ujson import loads

from asterisk_ng_server.exceptions import InvalidMethodParamsException
from asterisk_ng_server.exceptions import UnknownMethodException
from asterisk_ng_server.methods import METHODS


__all__ = [
    "asterisk_ng_controller",
]


class Headers(BaseModel):
    amouser_email: str
    amouser_id: int
    widget_version: str


class Command(BaseModel):
    jsonrpc: str
    id: int
    method: str
    params: Mapping[str, Any] = {}


def make_response_with_result(result: Mapping[str, Any], command_id: int) -> JSONResponse:
    response = {
        "headers": {
            "status_code": 200,
            "detail": "success"
        },
        "content": {
            "jsonrpc": "2.0",
            "result": {
                "result": result,
            },
            "id": command_id,
        }
    }
    return JSONResponse(response)


def make_response_with_exception(exception: str, command_id: int) -> JSONResponse:
    response = {
        "headers": {
            "status_code": 200,
            "detail": "success"
        },
        "content": {
            "jsonrpc": "2.0",
            "result": {
                "exception_name": exception,
            },
            "id": command_id,
        }
    }
    return JSONResponse(response)


async def asterisk_ng_controller(json: str = Form()) -> JSONResponse:

    # This code should be in middleware.
    # FastAPI and does not allow this to be done.
    # See https://github.com/tiangolo/fastapi/issues/191

    # -------------------------------------------------------------

    try:
        body = loads(json)

        json_headers = body.get("headers") or {}
        json_content = body.get("content") or {}

        headers = Headers(**json_headers)
        command = Command(**json_content)
    except (KeyError, ValidationError):
        return JSONResponse(
            content={
                "headers": {
                    "status_code": 400,
                    "detail": "Bad Request."
                }
            }
        )

    # Checking version compatibility.
    if headers.widget_version not in ["1.0.0"]:
        return JSONResponse(
            content={
                "headers": {
                    "status_code": 409,
                    "detail": "Incompatible version of the widget."
                }
            }
        )

    # -------------------------------------------------------------

    print(f"Request: {repr(headers)}, {repr(command)}.")

    try:
        method = METHODS[command.method]
    except KeyError:
        raise UnknownMethodException(command.method)

    try:
        result = await method(headers.amouser_email, headers.amouser_id, **command.params)
    except TypeError:
        raise InvalidMethodParamsException(command.method, command.params)
    except Exception as exc:
        exc_name = exc.__class__.__name__
        response = make_response_with_exception(exc_name, command_id=command.id)
        print(f"Response: {response.body}.")
        return response
    else:
        response = make_response_with_result(result, command_id=command.id)
        print(f"Response: {response.body}.")
        return response
