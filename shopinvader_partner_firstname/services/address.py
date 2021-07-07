# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _validator_create(self):
        schema = super()._validator_create()
        schema.update(
            {
                "name": {
                    "type": "string",
                    "required": True,
                    "excludes": ["firstname", "lastname"],
                },
                "firstname": {
                    "type": "string",
                    "required": True,
                    "excludes": "name",
                },
                "lastname": {
                    "type": "string",
                    "required": True,
                    "excludes": "name",
                },
            }
        )
        return schema

    def _json_parser(self):
        parser = super()._json_parser()
        parser.extend(["firstname", "lastname"])
        return parser
