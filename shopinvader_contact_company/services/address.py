# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _validator_create(self):
        res = super(AddressService, self)._validator_create()
        res["company"] = {"type": "string"}
        return res

    def _json_parser(self):
        res = super(AddressService, self)._json_parser()
        res.remove("name")
        res += ["contact_name:name", "company"]
        return res

    def _prepare_params(self, params):
        params = super(AddressService, self)._prepare_params(params)
        if "name" in params:
            params["contact_name"] = params.pop("name")
        return params
