import asyncio
from random import choices
from time import time
from typing import Any
from typing import Callable
from typing import Collection
from typing import Mapping
from uuid import UUID

from asterisk_ng_server.contacts import generate_contacts
from asterisk_ng_server.exceptions import LongPoolTimeout
from asterisk_ng_server.state import AgentStatus
from asterisk_ng_server.state import CallInfo
from asterisk_ng_server.state import SeverStateImpl
from asterisk_ng_server.state import Status

from .contacts import Contact


__all__ = [
    "METHODS",
]


server_state = SeverStateImpl()


CONTACTS = generate_contacts(40)
LAST_CONTACTS = CONTACTS[:15]
CONTACTS_MAPPING = {contact.uuid: contact for contact in CONTACTS}

METHODS: Mapping[str, Callable] = {}


def register(method: str):
    def _register(func):
        METHODS[method] = func
        return func
    return _register


def generate_unique_id() -> str:
    current_time = str(time())
    point_index = current_time.find('.')
    return current_time[0: point_index + 3]


def contact_to_mapping(contact: Contact) -> Mapping[str, Any]:
    return {
        "uuid": str(contact.uuid),
        "name": contact.name,
        "phone": contact.phone
    }


@register("ping")
async def ping(amouser_email: str, amouser_id: int) -> Mapping[str, Any]:
    return {"ping": "pong"}


@register("get_contacts")
async def get_contacts(
    amouser_email: str,
    amouser_id: int,
    start_with: str,
    max_results: int
) -> Collection[Mapping[str, Any]]:
    result = []
    for contact in CONTACTS:

        if len(result) == max_results:
            break

        lower_name = contact.name.lower()

        if lower_name.startswith(start_with.lower()) \
                or contact.phone.startswith(start_with):
            result.append(contact)

    return [contact_to_mapping(contact) for contact in result]


@register("get_last_contacts")
async def get_last_contacts(amouser_email: str, amouser_id: int, max_results: int) -> Collection[Mapping[str, Any]]:
    last_contacts = choices(LAST_CONTACTS, k=max_results)
    return [contact_to_mapping(contact) for contact in last_contacts]


@register("get_agent_status")
async def get_agent_status(amouser_email: str, amouser_id: int, current_status: Mapping[str, Any] = None) -> Mapping[str, Any]:
    current_client_state = AgentStatus(**current_status)
    try:
        current_server_state = await server_state.get_agent_status(amouser_id)
    except KeyError:
        await server_state.set_agent_status(amouser_id, AgentStatus(status=Status.NOT_CONVERSATION))
        return AgentStatus(status=Status.NOT_CONVERSATION).dict()
    if current_client_state == current_server_state:
        try:
            agent_status = await server_state.get_status_difference(amouser_id, timeout=8.0)
        except asyncio.TimeoutError:
            raise LongPoolTimeout()
        return agent_status.dict()

    return current_server_state.dict()


@register("set_mute")
async def mute(amouser_email: str, amouser_id: int, is_mute: bool) -> None:
    agent_status = await server_state.get_agent_status(amouser_id)
    agent_status.call_info.is_mute = is_mute
    await server_state.set_agent_status(amouser_id, agent_status)
    print(f"Set mute amouser_id: `{amouser_id:}` mute: {is_mute}.")


@register("set_hold")
async def enable_hold(amouser_email: str, amouser_id: int, is_hold) -> None:
    agent_status = await server_state.get_agent_status(amouser_id)
    agent_status.call_info.is_hold = is_hold
    await server_state.set_agent_status(amouser_id, agent_status)
    print(f"Set hold amouser_id: `{amouser_id:}` hold: {is_hold}.")


@register("originate")
async def originate(amouser_email: str, amouser_id: int, phone: str):
    new_aget_status = AgentStatus(
        status=Status.CONVERSATION,
        call_info=CallInfo(
            unique_id=generate_unique_id(),
            contact_name=None,
            contact_phone=phone,
            timestamp=int(time()),
        )
    )
    await server_state.set_agent_status(amouser_id, new_aget_status)
    print(f"Origination completed.")


@register("originate_by_contact")
async def originate_by_contact(amouser_email: str, amouser_id: int, contact_uuid: str):
    contact = CONTACTS_MAPPING[UUID(contact_uuid)]

    new_aget_status = AgentStatus(
        status=Status.CONVERSATION,
        call_info=CallInfo(
            unique_id=generate_unique_id(),
            contact_name=contact.name,
            contact_phone=contact.phone,
            timestamp=int(time()),
        )
    )
    await server_state.set_agent_status(amouser_id, new_aget_status)
    print(f"Origination by contact`s uuid completed.")


@register("redirect")
async def redirect(amouser_email: str, amouser_id: int, phone: str) -> None:
    await server_state.set_agent_status(amouser_id, AgentStatus(status=Status.NOT_CONVERSATION))
    print(f"Redirect completed: `{amouser_id}` -> `{phone}`.")


@register("hangup")
async def hangup(amouser_email: str, amouser_id: int) -> None:
    await server_state.set_agent_status(amouser_id, AgentStatus(status=Status.NOT_CONVERSATION))
    print(f"Hangup amouser_id: `{amouser_id}`.")
