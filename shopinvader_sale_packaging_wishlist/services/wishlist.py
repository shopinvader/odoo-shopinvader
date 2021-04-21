# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class WishlistService(Component):
    _name = "shopinvader.wishlist.service"
    _inherit = [
        "shopinvader.wishlist.service",
        "shopinvader.packaging.service.mixin",
    ]

    def _validator_line_schema(self):
        res = super()._validator_line_schema()
        res.update(self._validator_packaging_info())
        return res

    def _json_parser_line(self):
        return super()._json_parser_line() + self._json_parser_line_packaging()

    def _json_parser_line_packaging(self):
        return [
            (
                "product_id:packaging_by_qty",
                self._json_parser_product_packaging,
            ),
            (
                "product_packaging_id:packaging",
                lambda rec, fname: self._packaging_to_json(rec[fname]),
            ),
            "product_packaging_qty:packaging_qty",
        ]

    def _json_parser_product_packaging(self, rec, fname):
        return self._packaging_info_by_qty(rec.product_id, rec.quantity)

    def _prepare_item(self, record, params):
        res = super()._prepare_item(record, params)
        pkg_params = self._packaging_values_from_params(params)
        if pkg_params:
            res.update(pkg_params)
        return res

    def _packaging_values_from_params(self, params):
        res = super()._packaging_values_from_params(params)
        if "product_packaging" in res:
            # On sale.order.line they named a m2o field w/out `_id` :/
            res["product_packaging_id"] = res.pop("product_packaging")
        return res
