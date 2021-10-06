# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _name = "shopinvader.abstract.sale.service"
    _inherit = [
        "shopinvader.abstract.sale.service",
        "shopinvader.packaging.service.mixin",
    ]

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        pkg_vals = {
            "packaging": None,
            "packaging_qty": 0.0,
            "packaging_by_qty": [],
        }
        if line.product_packaging:
            pkg_vals = line.jsonify(self._parser_line_packaging(), one=True)
        res.update(pkg_vals)
        return res

    def _parser_line_packaging(self):
        return [
            (
                "product_packaging:packaging",
                lambda rec, fname: self._packaging_to_json(rec[fname]),
            ),
            ("product_packaging_qty:packaging_qty"),
            (
                "product_packaging_qty:packaging_by_qty",
                self._parser_packaging_by_qty,
            ),
        ]

    def _parser_packaging_by_qty(self, rec, fname):
        return self._packaging_info_by_qty(rec.product_id, rec.product_uom_qty)
