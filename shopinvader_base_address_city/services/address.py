# Copyright 2022 KMEE (http://www.kmee.com.br).
# @author Cristiano Rodrigues <cristiano.rodrigues@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _json_parser(self):
        res = super()._json_parser()

        res.append(("city_id", ["id", "name"]))

        return res

    def _validator_create(self):
        res = super()._validator_create()

        if "city" in res:
            del res["city"]

        res["city_id"] = {
            "type": "dict",
            "schema": {
                "id": {
                    "coerce": to_int,
                    "nullable": False,
                    "type": "integer",
                },
                "name": {
                    "type": "string",
                    "nullable": True,
                },
            },
        }

        return res

    def _prepare_params(self, params, mode="create"):
        if params.get("city_id"):
            params["city_id"] = (
                params.get("city_id")["id"]
                if type(params["city_id"]) == dict
                else params.get("city_id")
            )
        return super(AddressService, self)._prepare_params(params, mode)
