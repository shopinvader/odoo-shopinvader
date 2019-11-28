# Copyright 2019 Camptocamp (http://www.camptocamp.com)
# Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CustomerService(Component):
    _inherit = "shopinvader.customer.service"

    def _validator_create(self):
        schema = super()._validator_create()
        schema.update(
            {
                # TODO: now all the fields are not required.
                # Is it possible (desireadable?) to make name required
                # if the others are not passed and viceversa.
                "name": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                },
                "firstname": {"type": "string", "required": False},
                "lastname": {"type": "string", "required": False},
            }
        )
        return schema

    def _prepare_params(self, params, mode="create"):
        params = super()._prepare_params(params, mode=mode)
        # make sure name is not passed to create, even empty,
        # otherwise partner creation will be broken
        if params.get("firstname") and params.get("lastname"):
            params.pop("name", None)
        return params


class AddressService(Component):
    _inherit = "shopinvader.address.service"

    def _json_parser(self):
        parser = super()._json_parser()
        parser.extend(["firstname", "lastname"])
        return parser
