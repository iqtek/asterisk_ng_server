import asyncio

from collections import defaultdict
from enum import Enum

from typing import MutableSequence
from typing import MutableMapping
from typing import Optional

from pydantic import BaseModel


__all__ = [
    "Status",
    "CallInfo",
    "AgentStatus",
    "ISeverState",
    "SeverStateImpl",
]


class Status(Enum):
    CONVERSATION: 'Status' = "CONVERSATION"
    NOT_CONVERSATION: 'Status' = "NOT_CONVERSATION"


class CallInfo(BaseModel):
    unique_id: str
    contact_name: Optional[str] = None
    contact_phone: str
    is_hold: bool = False
    is_mute: bool = False
    timestamp: int


class AgentStatus(BaseModel):
    status: Status = Status.NOT_CONVERSATION
    call_info: Optional[CallInfo] = None

    class Config:
        use_enum_values = True


class ISeverState:

    __slots__ = ()

    async def set_agent_status(self, user_id: int, status: AgentStatus) -> None:
        raise NotImplementedError()

    async def get_agent_status(self, user_id: int) -> AgentStatus:
        raise NotImplementedError()

    async def get_status_difference(self, user_id: int, timeout: float = 10) -> AgentStatus:
        raise NotImplementedError()


class SeverStateImpl(ISeverState):

    __slots__ = (
        "__server_state",
        "__futures",
    )

    def __init__(self) -> None:
        self.__server_state: MutableMapping[int, AgentStatus] = {}
        self.__futures: MutableMapping[int, MutableSequence[asyncio.Future[AgentStatus]]] = defaultdict(list)

    async def set_agent_status(self, user_id: int, status: AgentStatus) -> None:
        self.__server_state[user_id] = status
        if user_id in self.__futures.keys():
            futures = self.__futures[user_id]
            for future in futures:
                try:
                    future.set_result(status)
                except asyncio.exceptions.InvalidStateError:
                    pass
            futures.clear()

    async def get_agent_status(self, user_id: int) -> AgentStatus:
        agent_status = self.__server_state[user_id]
        return agent_status.copy()

    async def get_status_difference(self, user_id: int, timeout: float = 10) -> AgentStatus:
        future: asyncio.Future[AgentStatus] = asyncio.Future()
        self.__futures[user_id].append(future)
        return await asyncio.wait_for(future, timeout=timeout)
