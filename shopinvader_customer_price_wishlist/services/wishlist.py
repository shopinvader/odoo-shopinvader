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

    # TODO: if we had a centralized way to retrieve prices for customers
    # we could avoid this module completely.
    def _json_parser_product(self):
        res = super()._json_parser_product()
        res = [x for x in res if x != "price"]
        res.append(("price", self._json_parser_product_price))
        return res

    def _json_parser_product_price(self, rec, fname):
        return self.customer_price_service._get_price(rec, fname)

    # FIXME: this method does not exist in 13.0. It will be introduced by
    # https://github.com/shopinvader/odoo-shopinvader/pull/783
    # If you want to use all recent features this is required to not break it.
    # It's harmless as it's called only when used w/ #783.
    # When #783 will be merged, `_json_parser_product` must be dropped.
    def _json_parser_product_data(self, rec, fname):
        res = super()._json_parser_product_data(rec, fname)
        res["price"] = self._json_parser_product_price(
            rec.shopinvader_variant_id, fname
        )
        return res
