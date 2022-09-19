from random import choice
from random import randint
from uuid import uuid4

from pydantic import BaseModel
from pydantic import UUID4


__all__ = [
    "Contact",
    "generate_contacts",
]


NAMES = [
    "Harry",
    "Rose",
    "Larry",
    "Alex",
    "Julie",
    "Boris",
    "Petr",
    "Eric",
    "Mark",
]


SURNAMES = [
    "Williams",
    "Peters",
    "Gibson",
    "Martin",
    "Jordan",
    "Jackson",
    "Grant",
    "Davis",
    "Collins",
    "Bradley",
    "Barlow",
]


class Contact(BaseModel):
    uuid: UUID4
    name: str
    phone: str


def generate_random_phone() -> str:
    return str(randint(7, 8)) + ''.join([str(randint(0, 9)) for _ in range(9)])


def generate_contacts(count: int = 20):

    result = []

    for _ in range(count):
        name = f"{choice(NAMES)} {choice(SURNAMES)}"
        phone = generate_random_phone()
        contact = Contact(uuid=uuid4(), name=name, phone=phone)
        result.append(contact)

    return result
