# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _validator_create(self):
        res = super()._validator_create()
        res.update(
            {
                "invoicing_mode": {"type": "string", "required": False},
            }
        )
        return res

    def _json_parser(self):
        res = super()._json_parser()
        res.append("invoicing_mode")
        return res
