# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.extendable_fastapi import StrictExtendableBaseModel
from odoo.addons.shopinvader_schema_address.schemas import ShippingAddress


class ShippingInfo(StrictExtendableBaseModel):
    address: ShippingAddress | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        return cls.model_construct(
            address=(ShippingAddress.from_res_partner(odoo_rec.partner_shipping_id))
        )
