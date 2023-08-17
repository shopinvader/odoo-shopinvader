# Copyright 2022 KMEE (http://www.kmee.com.br).
# @author Cristiano Rodrigues <cristiano.rodrigues@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _json_parser(self):
        res = super()._json_parser()

        res.append("district")
        res.append("street_number")
        res.append("street_name")
        # res.append("email")
        res.remove("street")

        return res

    def _validator_create(self):
        res = super()._validator_create()

        if "street" in res:
            del res["street"]

        del res["state"]

        res["zip"]["required"] = False
        res["country"]["required"] = False

        res["district"] = {
            "type": "string",
            "required": False,
        }
        res["street_number"] = {
            "type": "string",
            "required": False,
        }
        res["street_name"] = {
            "type": "string",
            "required": False,
        }
        # res["email"] = {
        #     "type": "string",
        #     "required": False,
        # }

        return res

    def _validator_update(self):
        res = super()._validator_update()
        return res
