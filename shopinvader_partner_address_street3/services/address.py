# Copyright 2021 David BEAL @ Akretion
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _json_parser(self):
        parser = super()._json_parser()
        parser.append("street3")
        return parser

    def _validator_create(self):
        schema = super()._validator_create()
        schema["street3"] = {"type": "string", "nullable": True}
        return schema
