# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import pydantic

from typing import Optional

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
    street2: Optional[str] = None
    zip: str
    city: str
    phone: Optional[str] = None
    email: Optional[str] = None
    state: Optional[State] = pydantic.Field(alias="state_id") or None
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
