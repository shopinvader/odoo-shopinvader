# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    shop_only_quotation = fields.Boolean(
        string="Shopinvader: Only for Quotation",
        compute="_compute_shop_only_quotation",
        inverse="_inverse_shop_only_quotation",
        store=True,
    )

    @api.depends("product_variant_ids.shop_only_quotation")
    def _compute_shop_only_quotation(self):
        # True only if true for all its variants
        for rec in self:
            rec.shop_only_quotation = (
                all(rec.product_variant_ids.mapped("shop_only_quotation"))
                if rec.product_variant_ids
                else False
            )

    def _inverse_shop_only_quotation(self):
        # Sets the value on all its variants
        for rec in self:
            rec.product_variant_ids.shop_only_quotation = rec.shop_only_quotation

    def _create_variant_ids(self):
        # Make sure new variants have the same value than the template.
        templates = self.filtered("shop_only_quotation")
        res = super()._create_variant_ids()
        products = templates.product_variant_ids.filtered(
            lambda rec: not rec.shop_only_quotation
        )
        products.shop_only_quotation = True
        return res
