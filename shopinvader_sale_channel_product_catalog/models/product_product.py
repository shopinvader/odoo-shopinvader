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

    def _add_to_cart_allowed(self, backend, partner=None):
        """Check if you can add current product to a cart."""
        # no super() here because we don't have any shopinvader.variant
        # anymore
        return backend.sale_channel_id.is_add_to_sol_authorized(self)

    def _get_invader_variant(self, backend, lang):
        """deprecated
        now a variant is a product.product

        :param backend: backend recordset
        :param lang: lang code
        no lang anymore
        """
        return self._add_to_cart_allowed(backend) and self

    def get_shop_data(self):
        return self._get_shop_data()

    # rest_api way ?
    def _get_shop_data(self):
        """Compute shop data jsonifier parser."""
        exporter = self._jsonify_get_exporter()
        return self.jsonify(exporter.get_json_parser(), one=True)

    def _jsonify_get_exporter(self):
        return self.env.ref("shopinvader.ir_exp_shopinvader_variant").sudo()
