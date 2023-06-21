# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class AddressSearch(BaseModel, metaclass=ExtendableModelMeta):
    """
    TODO: improve
        used to search address on model res partner
        state is state's name or code
        country is country's name or code
    """

    name: str | None
    street: str | None
    street2: str | None
    zip: str | None
    city: str | None
    phone: str | None
    email: str | None
    state: str | None
    country: str | None
    type: str | None


class AddressInput(BaseModel, metaclass=ExtendableModelMeta):
    """
    TODO: improve
        used to create new address (res.partner)
        state and country can be name or code
    """

    name: str
    street: str
    street2: str | None
    zip: str
    city: str
    phone: str | None
    email: str | None
    state: str | None
    country: str | None
    type: str

class AddressUpdate(BaseModel, metaclass=ExtendableModelMeta):
    """
    TODO: improve
        used to update address (res.partner)
        state and country can be name or code
    """

    name: str | None
    street: str | None
    street2: str | None
    zip: str | None
    city: str | None
    phone: str | None
    email: str | None
    state: str | None
    country: str | None
