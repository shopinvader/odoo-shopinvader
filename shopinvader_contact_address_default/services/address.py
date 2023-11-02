# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _validator_create(self):
        res = super()._validator_create()
        res.update(
            {
                "partner_invoice_id": {
                    "type": "integer",
                    "required": False,
                    "nullable": True,
                    "coerce": to_int,
                },
                "partner_shipping_id": {
                    "type": "integer",
                    "required": False,
                    "nullable": True,
                    "coerce": to_int,
                },
            }
        )
        return res

    def _json_parser(self):
        res = super()._json_parser()
        res += [
            ("partner_invoice_id", ["id", "display_name"]),
            ("partner_shipping_id", ["id", "display_name"]),
        ]
        return res
