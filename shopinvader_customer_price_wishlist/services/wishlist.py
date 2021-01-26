# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class WishlistService(Component):
    _inherit = "shopinvader.wishlist.service"

    _customer_price_service = None

    @property
    def customer_price_service(self):
        if self._customer_price_service:
            return self._customer_price_service
        self._customer_price_service = self.component(usage="customer_price")
        return self._customer_price_service

    def _json_parser_product_price(self, rec, fname):
        return self.customer_price_service._get_price(rec, fname)

    # TODO: if we had a centralized way to retrieve prices for customers
    # we could avoid this module completely.
    def _json_parser_product_data(self, rec, fname):
        res = super()._json_parser_product_data(rec, fname)
        res["price"] = self._json_parser_product_price(
            rec.shopinvader_variant_id, fname
        )
        return res
