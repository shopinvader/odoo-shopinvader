# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import pydantic
from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils


class State(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str
    code: str

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class Country(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str
    code: str

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class Address(BaseModel, metaclass=ExtendableModelMeta):
    name: str
    street: str
    street2: str | None = None
    zip: str
    city: str
    phone: str | None = None
    email: str | None = None
    state: State | None = pydantic.Field(alias="state_id")
    country: Country = pydantic.Field(alias="country_id")

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter


class BillingAddress(Address):
    """
    Billing Address
    """


class ShippingAddress(Address):
    """
    Shipping Address
    """
