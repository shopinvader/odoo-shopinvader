# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _validator_create(self):
        res = super()._validator_create()
        res["siret"] = {"type": "string", "required": False}
        return res

    def _json_parser(self):
        return super()._json_parser() + ["siret"]
