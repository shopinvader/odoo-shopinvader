# Copyright 2023 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    shopinvader_backend_ids = fields.Many2many(
        comodel_name="shopinvader.backend",
        compute="_compute_shopinvader_backend_ids",
        store=False,
    )

    def _compute_shopinvader_backend_ids(self):
        # product is multiple catalog
        # catalog is associated to multiple channels
        # a catalog
        for rec in self:
            rec.shopinvader_backend_ids = (
                rec.product_catalog_ids.shopinvader_backend_ids
            )

    # TODO: _add_to_cart_allowed,_check_allowed_product,_add_item
    # are also in shopinvader_product_binding
    def _add_to_cart_allowed(self, backend, partner=None):
        """Check if you can add current product to a cart."""
        return backend.sale_channel_id.is_add_to_sol_authorized(self)
