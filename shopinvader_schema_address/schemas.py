# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import ExtendableModelMeta
from pydantic import BaseModel

from odoo.addons.pydantic import utils


class Address(BaseModel, metaclass=ExtendableModelMeta):
    id: int
    name: str | None
    street: str | None
    street2: str | None
    zip: str | None
    city: str | None
    phone: str | None
    email: str | None
    state_id: int | None
    country_id: int | None

    class Config:
        orm_mode = True
        getter_dict = utils.GenericOdooGetter

    @classmethod
    def from_res_partner(cls, odoo_rec):
        res = cls.construct()

        res.id = odoo_rec.id
        res.name = odoo_rec.name or None
        res.street = odoo_rec.street or None
        res.street2 = odoo_rec.street or None
        res.zip = odoo_rec.zip or None
        res.city = odoo_rec.city or None
        res.phone = odoo_rec.phone or None
        res.email = odoo_rec.email or None
        res.state_id = odoo_rec.state_id.id or None
        res.country_id = odoo_rec.country_id.id or None

        return res


class BillingAddress(Address):
    """
    Billing Address
    """
    vat: str | None

    @classmethod
    def from_res_partner(cls, odoo_rec):
        res = super().from_res_partner(odoo_rec)
        res.vat = odoo_rec.vat

        return res


class ShippingAddress(Address):
    """
    Shipping Address
    """
