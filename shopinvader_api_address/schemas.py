# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel


class AddressInput(BaseModel, metaclass=ExtendableModelMeta):
    """
    TODO: improve
        used to create new address (res.partner)
        state and country can be name or code
    """

    name: str | None
    street: str | None
    street2: str | None
    zip: str | None
    city: str | None
    phone: str | None
    email: str | None
    state: int | None
    country: int | None


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
    state: int | None
    country: int | None
