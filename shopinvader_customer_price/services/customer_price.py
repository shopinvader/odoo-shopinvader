# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.osv import expression

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class CustomerPriceService(Component):
    """Shopinvader service to expose customer specific product prices."""

    _name = "shopinvader.customer.price.service"
    _inherit = "base.shopinvader.service"
    _usage = "customer_price"
    _expose_model = "shopinvader.variant"
    _description = __doc__

    def products(self, **params):
        domain = expression.normalize_domain(self._get_base_search_domain())
        domain = expression.AND([domain, [("record_id", "in", params["ids"])]])
        records = self.env[self._expose_model].search(domain)
        return self._to_json(records, one=params.get("one"))

    def _validator_products(self):
        return {
            "ids": {
                "type": "list",
                "nullable": True,
                "required": True,
                "schema": {"coerce": to_int, "type": "integer"},
            },
            "one": {"type": "boolean", "nullable": True, "required": False},
        }

    def _get_base_search_domain(self):
        if not self._is_logged_in():
            return expression.FALSE_DOMAIN
        return super()._get_base_search_domain()

    def _to_json(self, records, **kw):
        return records.jsonify(self._json_parser(), **kw)

    def _json_parser(self):
        return [
            "id",
            ("record_id:objectID", lambda rec, fname: rec[fname].id),
            ("price", self._get_price),
        ]

    def _get_price(self, record, fname):
        pricelist = self.shopinvader_backend._get_cart_pricelist(self.partner)
        fposition = self.shopinvader_backend._get_fiscal_position(self.partner)
        company = self.shopinvader_backend.company_id
        return {
            self.invader_partner.role: record._get_price(
                pricelist=pricelist, fposition=fposition, company=company
            )
        }
