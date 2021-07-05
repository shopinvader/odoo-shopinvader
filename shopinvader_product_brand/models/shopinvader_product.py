# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ShopinvaderProduct(models.Model):
    _inherit = "shopinvader.product"

    shopinvader_brand_id = fields.Many2one(
        "shopinvader.brand",
        compute="_compute_shopinvader_brand_id",
        string="Shopinvader Brand",
    )

    @api.depends("product_brand_id.shopinvader_bind_ids")
    def _compute_shopinvader_brand_id(self):
        for record in self:
            shopinvader_brand = record.product_brand_id.shopinvader_bind_ids.filtered(
                lambda s: s.backend_id == record.backend_id
                and s.lang_id == record.lang_id
            )
            if len(shopinvader_brand) > 1:
                _logger.error("Too many shopinvader_brand found take the first one")
            record.shopinvader_brand_id = fields.first(shopinvader_brand)
