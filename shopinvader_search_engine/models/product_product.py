# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "se.indexable.record"]

    @api.model
    def _get_shopinvader_product_variants(self, product_ids):
        variants = super()._get_shopinvader_product_variants(product_ids)
        variants = variants._filter_by_index()
        return variants

    @api.depends_context("index")
    def _compute_main_product(self):
        return super()._compute_main_product()
