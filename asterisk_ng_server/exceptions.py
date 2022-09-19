from typing import Any
from typing import Mapping


__all___ = [
    "InvalidMethodParamsException",
    "UnknownMethodException",
    "IncorrectStateException",
    "LongPoolTimeout",
]


class UnknownMethodException(Exception):

    __slots__ = ()

    def __init__(self, method: str):
        self.method = method


class InvalidMethodParamsException(Exception):

    __slots__ = ()

    def __init__(self, method: str, params: Mapping[str, Any]):
        self.method = method
        self.params = params


class LongPoolTimeout(Exception):
    pass
