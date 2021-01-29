# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=method-required-super, consider-merging-classes-inherited

from odoo import _
from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component
from odoo.exceptions import AccessError

from .. import shopinvader_response


class AddressService(Component):
    _inherit = "base.shopinvader.service"
    _name = "shopinvader.address.service"
    _usage = "addresses"
    _expose_model = "res.partner"

    # The following method are 'public' and can be called from the controller.

    def get(self, _id):
        return self._to_json(self._get(_id))

    def search(self, **params):
        if not self.partner:
            return {"data": []}
        else:
            return self._paginate_search(**params)

    # pylint: disable=W8106
    def create(self, **params):
        params["parent_id"] = self.partner.id
        if not params.get("type"):
            params["type"] = "other"
        self.env["res.partner"].create(self._prepare_params(params))
        return self.search()

    def update(self, _id, **params):
        address = self._get(_id)
        address.write(self._prepare_params(params))
        res = self.search()
        if address.address_type == "profile":
            customer = self.component(usage="customer")
            response = shopinvader_response.get()
            customer_data = customer._to_customer_info(address)
            response.set_store_cache("customer", customer_data)
        return res

    def delete(self, _id):
        address = self._get(_id)
        if self.partner == address:
            raise AccessError(_("Can not delete the partner account"))
        address.active = False
        return self.search()

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    # Validator
    def _get_allowed_type(self):
        return ["contact", "invoice", "delivery", "other", "private"]

    def _validator_search(self):
        validator = self._default_validator_search()
        validator.pop("domain", {})
        return validator

    def _validator_create(self):
        res = {
            "name": {"type": "string", "required": True},
            "type": {
                "type": "string",
                "allowed": self._get_allowed_type(),
                "empty": False,
            },
            "street": {"type": "string", "required": True, "empty": False},
            "street2": {"type": "string", "nullable": True},
            "zip": {"type": "string", "required": True, "empty": False},
            "city": {"type": "string", "required": True, "empty": False},
            "phone": {"type": "string", "nullable": True, "empty": False},
            "mobile": {"type": "string", "nullable": True, "empty": False},
            "state": {
                "type": "dict",
                "schema": {
                    "id": {
                        "coerce": to_int,
                        "nullable": True,
                        "type": "integer",
                    }
                },
            },
            "country": {
                "required": True,
                "type": "dict",
                "schema": {
                    "id": {
                        "coerce": to_int,
                        "required": True,
                        "nullable": False,
                        "type": "integer",
                    }
                },
            },
            "is_company": {"coerce": to_bool, "type": "boolean"},
            "opt_in": {"coerce": to_bool, "type": "boolean"},
            "opt_out": {"coerce": to_bool, "type": "boolean"},
        }
        return res

    def _validator_update(self):
        res = self._validator_create()
        for key in res:
            if "required" in res[key]:
                del res[key]["required"]
        return res

    def _validator_delete(self):
        return {}

    def _get_base_search_domain(self):
        return [("id", "child_of", self.partner.id)]

    def _json_parser(self):
        res = [
            "id",
            "display_name",
            "name",
            "ref",
            "street",
            "street2",
            "zip",
            "city",
            "phone",
            "mobile",
            "opt_in",
            "opt_out",
            "vat",
            "type",
            ("state_id:state", ["id", "name", "code"]),
            ("country_id:country", ["id", "name", "code"]),
            "address_type",
            "is_company",
        ]
        return res

    def _to_json(self, address):
        return address.jsonify(self._json_parser())

    def _prepare_params(self, params):
        for key in ["country", "state"]:
            if key in params:
                val = params.pop(key)
                if val.get("id"):
                    params["%s_id" % key] = val["id"]
        return params
