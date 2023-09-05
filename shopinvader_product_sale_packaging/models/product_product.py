# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.base_sparse_field.models.fields import Serialized


class ProductProduct(models.Model):
    _inherit = "product.product"

    packaging = Serialized(
        compute="_compute_packaging",
        help="Technical field to store packaging for the shop",
        store=True,
    )

    @api.depends(lambda self: self._compute_packaging_depends())
    def _compute_packaging(self):
        for rec in self:
            rec.packaging = rec._get_variant_packaging()

    def _compute_packaging_depends(self):
        return (
            "sell_only_by_packaging",
            "packaging_ids.qty",
            "packaging_ids.can_be_sold",
            "packaging_ids.shopinvader_display",
            "packaging_ids.barcode",
            "packaging_ids.packaging_level_id.name",
        )

    def _get_variant_packaging(self):
        res = []
        ctx = self._get_variant_packaging_ctx()
        rec = self.with_context(**ctx)
        contained_mapping = rec.packaging_contained_mapping or {}
        packaging = rec._ordered_packaging()
        can_be_sold_info = {
            x["id"]: x["can_be_sold"] for x in self.packaging_ids.read(["can_be_sold"])
        }
        for pkg in packaging:
            pkg_info = self._prepare_qty_by_packaging_values(pkg, pkg.qty)
            pkg_info["contained"] = contained_mapping.get(str(pkg.id))
            pkg_info["can_be_sold"] = can_be_sold_info.get(pkg.id, False)
            if pkg.is_unit:
                pkg_info["can_be_sold"] = not self.sell_only_by_packaging
            res.append(pkg_info)
        return res

    def _get_variant_packaging_ctx(self):
        return {
            # consider only packaging that can be displayed
            "_packaging_filter": lambda x: x.shopinvader_display,
            "_packaging_values_handler": self._prepare_qty_by_packaging_values,
        }

    def _prepare_qty_by_packaging_values(self, packaging, qty_per_pkg):
        # TODO: why re-define? Duplicate of stock_packaging_calculator/models/product.py L147
        return {
            "id": packaging.id,
            "qty": qty_per_pkg,
            "name": packaging.name,
            "is_unit": packaging.is_unit,
            "barcode": packaging.barcode,
        }
