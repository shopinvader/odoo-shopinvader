# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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
    id: int
    name: str
    street: str
    street2: str | None
    zip: str
    city: str
    phone: str | None
    email: str | None
    state: State | None
    country: Country
    type: str

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter

    @classmethod
    def from_orm(cls, odoo_rec):
        res = cls.construct()

        res.id = odoo_rec.id
        res.name = odoo_rec.name
        res.street = odoo_rec.street
        res.street2 = odoo_rec.street or None
        res.zip = odoo_rec.zip
        res.city = odoo_rec.city
        res.phone = odoo_rec.phone or None
        res.email = odoo_rec.email or None
        res.state = State.from_orm(odoo_rec.state_id) if odoo_rec.state_id else None
        res.country = (
            Country.from_orm(odoo_rec.country_id) if odoo_rec.country_id else None
        )
        res.type = odoo_rec.type

        return res


class BillingAddress(Address):
    """
    Billing Address
    """


class ShippingAddress(Address):
    """
    Shipping Address
    """
