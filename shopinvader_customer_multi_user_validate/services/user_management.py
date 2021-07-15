# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.shopinvader_customer_validate.models.shopinvader_partner import (
    ALL_STATES,
)


class UsersService(Component):
    _inherit = "shopinvader.users.service"

    def _validator_update(self):
        res = super()._validator_update()
        res["state"] = {
            "type": "string",
            "required": False,
            "allowed": ALL_STATES,
        }
        return res

    def _json_parser(self):
        return super()._json_parser() + ["state"]
