# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _validator_create(self):
        schema = super(CustomerService, self)._validator_create()
        schema["street3"] = {"type": "string", "required": False}
        return schema


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _json_parser(self):
        parser = super(AddressService, self)._json_parser()
        parser.append("street3")
        return parser

    def _validator_create(self):
        schema = super(AddressService, self)._validator_create()
        schema["street3"] = {"type": "string", "required": False}
        return schema
