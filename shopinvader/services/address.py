# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=method-required-super, consider-merging-classes-inherited

from odoo import _
from odoo.exceptions import AccessError

from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component

from .. import shopinvader_response


class AddressService(Component):
    """Shopinvader service to create and edit customers' addresses."""

    _inherit = [
        "base.shopinvader.service",
        "shopinvader.partner.service.mixin",
    ]
    _name = "shopinvader.address.service"
    _usage = "addresses"
    _expose_model = "res.partner"
    _description = __doc__

    # The following method are 'public' and can be called from the controller.

    def get(self, _id):
        return self._to_address_info(_id)

    def search(self, **params):
        if not self.partner:
            return {"data": []}
        else:
            return self._paginate_search(**params)

    # pylint: disable=W8106
    def create(self, **params):
        params["parent_id"] = self.partner.id
        partner = self.env["res.partner"].create(self._prepare_params(params))
        self._post_create(partner)
        return self.search()

    def update(self, _id, **params):
        address = self._get(_id)
        address.write(self._prepare_params(params, mode="update"))
        res = self.search()
        if self._store_cache_needed(address):
            res["store_cache"] = {"customer": self._to_json(address)[0]}
            customer = self.component(usage="customer")
            response = shopinvader_response.get()
            customer_data = customer._to_customer_info(address)
            response.set_store_cache("customer", customer_data)

        self._post_update(address)
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
    def _to_address_info(self, _id):
        return self._to_json(self._get(_id))

    def _store_cache_needed(self, partner):
        # TODO remove this kind of checks
        return partner.address_type == "profile"

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
                "default": "contact",
            },
            "street": {"type": "string", "required": True, "empty": False},
            "street2": {"type": "string", "nullable": True},
            "zip": {"type": "string", "required": True, "empty": False},
            "city": {"type": "string", "required": True, "empty": False},
            "phone": {"type": "string", "nullable": True, "empty": False},
            "email": {"type": "string", "required": False, "nullable": True},
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
            "title": {
                "required": False,
                "type": "dict",
                "schema": {
                    "id": {
                        "coerce": to_int,
                        "required": False,
                        "nullable": True,
                        "type": "integer",
                    }
                },
            },
            "industry_id": {
                "required": False,
                "type": "dict",
                "schema": {
                    "id": {
                        "coerce": to_int,
                        "required": False,
                        "nullable": True,
                        "type": "integer",
                    }
                },
            },
            "is_company": {"coerce": to_bool, "type": "boolean"},
            "opt_in": {"coerce": to_bool, "type": "boolean"},
            "opt_out": {"coerce": to_bool, "type": "boolean"},
            "lang": {"type": "string", "required": False},
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
        return self._default_domain_for_partner_records(
            # NOTE: here we must use `child_of` as default operator
            partner_field="id",
            operator="child_of",
            with_backend=False,
        )

    def _json_parser(self):
        res = [
            "id",
            ("parent_id", lambda rec, fname: rec.parent_id.id),
            "type",
            "display_name",
            "name",
            "ref",
            "street",
            "street2",
            "zip",
            "city",
            "phone",
            "email",
            "function",
            "opt_in",
            "is_blacklisted:opt_out",
            "vat",
            ("state_id:state", ["id", "name", "code"]),
            ("country_id:country", ["id", "name", "code"]),
            "address_type",
            "is_company",
            "lang",
            ("title", ["id", "name"]),
            "is_shopinvader_active:enabled",
            ("industry_id", ["id", "name"]),
        ]
        return res

    def _to_json(self, address, **kw):
        data = address.jsonify(self._json_parser())
        for item in data:
            # access info on the current record partner record
            item["access"] = self.access_info.for_address(item["id"])
        return data

    def _prepare_params(self, params, mode="create"):
        for key in ["country", "state"]:
            if key in params:
                val = params.pop(key)
                if val.get("id"):
                    params["%s_id" % key] = val["id"]
        # TODO: every field like m2o should be handled in the same way.
        # `country` and `state` are exceptions as they should match `_id`
        # naming already on client side as it has been done for industry.
        # Moreover, is weird that we send a dictionary containing and ID
        # instead of sending the ID straight.
        if params.get("industry_id"):
            params["industry_id"] = params.get("industry_id")["id"]
        if params.get("title"):
            params["title"] = params.get("title")["id"]

        return params
