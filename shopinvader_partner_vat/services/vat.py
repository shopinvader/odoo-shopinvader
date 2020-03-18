# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _
from odoo.addons.component.core import Component
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    import stdnum.eu.vat
except (ImportError, IOError) as err:
    _logger.debug(err)


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def check_vat(self, **params):
        partner_obj = self.env["res.partner"]
        country_code, vat_number = partner_obj._split_vat(params["vat_number"])
        vat_number = country_code.upper() + vat_number
        res = {
            "valid": partner_obj.simple_vat_check(country_code, vat_number),
            "vat_number": vat_number,
        }
        if self.shopinvader_backend.company_id.vat_check_vies and self.env[
            "res.country"
        ].search(
            [
                ("code", "=ilike", country_code),
                ("country_group_ids", "=", self.env.ref("base.europe").id),
            ]
        ):
            res = self._check_vat_vies(vat_number)

        return res

    def _check_vat_vies(self, vat_number):
        res = {"vat_number": vat_number}
        try:
            response = stdnum.eu.vat.check_vies(vat_number)
            if response["valid"]:
                res.update(
                    {
                        "with_details": True,
                        "name": response["name"],
                        "address": response["address"],
                        "valid": True,
                    }
                )
            else:
                res["valid"] = False
        except Exception as e:
            raise ValidationError(
                _("VIES server communication problem: {}".format(e))
            )
        return res

    # Validator
    def _validator_check_vat(self):
        return {"vat_number": {"type": "string"}}

    def _validator_return_check_vat(self):
        return {
            "valid": {"type": "boolean", "required": True},
            "vat_number": {"type": "string", "required": True},
            "name": {"type": "string", "required": False},
            "address": {"type": "string", "required": False},
            "with_details": {"type": "boolean", "required": False},
        }
