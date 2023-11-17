# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    shopinvader_price = fields.Json(compute="_compute_shopinvader_price")

    @api.depends_context("index_id")
    def _compute_shopinvader_price(self):
        index_id = self.env.context.get("index_id", False)
        index = self.env["se.index"].browse(index_id)
        for record in self:
            if index_id:
                prices = {}
                for sale_profile in index.backend_id.sale_profile_ids:
                    fposition = fields.first(sale_profile.fiscal_position_ids)
                    price = record._get_price(
                        pricelist=sale_profile.pricelist_id,
                        fposition=fposition,
                        company=index.backend_id.company_id,
                    )
                    prices.update({sale_profile.code: price})
            else:
                prices = {"default": record._get_price()}
            record.shopinvader_price = prices
