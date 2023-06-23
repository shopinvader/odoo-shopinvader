# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_api_address.schemas import (
    ShippingAddressCreate,
    ShippingAddressUpdate,
)
from odoo.addons.shopinvader_schema_address.schemas import ShippingAddress


class ShippingAddress(ShippingAddress, extends=ShippingAddress):
    """
    Shipping Address
    """

    shipping_note: str | None

    @classmethod
    def from_res_partner(cls, odoo_rec):
        res = super().from_res_partner(odoo_rec)
        res.shipping_note = odoo_rec.shipping_note or None

        return res


class ShippingAddressCreate(ShippingAddressCreate, extends=ShippingAddressCreate):
    """
    Creation of Shipping Address
    """

    shipping_note: str | None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()

        vals["shipping_note"] = self.shipping_note

        return vals


class ShippingAddressUpdate(ShippingAddressUpdate, extends=ShippingAddressUpdate):
    """
    Update of Shipping Address
    """

    shipping_note: str | None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()

        vals["shipping_note"] = self.shipping_note

        return vals
