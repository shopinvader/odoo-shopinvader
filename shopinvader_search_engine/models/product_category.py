# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "se.indexable.record"]

    shopinvader_parent_id = fields.Many2one(
        "product.category",
        "Shopinvader Parent",
        compute="_compute_parent_category",
    )
    shopinvader_child_ids = fields.Many2many(
        "product.category",
        "Shopinvader Childs",
        compute="_compute_child_category",
    )

    @api.depends_context("index_id")
    @api.depends("parent_id", "parent_id.se_binding_ids")
    def _compute_parent_category(self):
        for record in self:
            record.shopinvader_parent_id = (
                record.parent_id._filter_by_bound_in_same_lang()
            )

    @api.depends_context("index_id")
    @api.depends("child_id", "child_id.se_binding_ids")
    def _compute_child_category(self):
        for record in self:
            record.shopinvader_child_ids = (
                record.child_id._filter_by_bound_in_same_lang()
            )

    def _get_parent(self):
        self.ensure_one()
        return self.shopinvader_parent_id
