# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from extendable_pydantic import StrictExtendableBaseModel

from odoo.addons.shopinvader_schema_address.schemas import DeliveryAddress


class DeliveryInfo(StrictExtendableBaseModel):
    address: DeliveryAddress | None = None

    @classmethod
    def from_sale_order(cls, odoo_rec):
        return cls.model_construct(
            address=(DeliveryAddress.from_res_partner(odoo_rec.partner_shipping_id))
        )
