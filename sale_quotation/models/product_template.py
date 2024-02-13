# Copyright 2017-2018 Akretion (http://www.akretion.com).
# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    shop_only_quotation = fields.Selection(
        selection=[
            ("all_variant", "All Variant"),
            ("manually_on_variant", "Manually on Variant"),
            ("never", "Never"),
        ],
        string="Shopinvader: Only for Quotation",
        compute="_compute_shop_only_quotation",
        inverse="_inverse_shop_only_quotation",
        store=True,
    )

    @api.depends("product_variant_ids.shop_only_quotation")
    def _compute_shop_only_quotation(self):
        # True only if true for all its variants
        for rec in self:
            if not rec.product_variant_ids or not any(
                rec.product_variant_ids.mapped("shop_only_quotation")
            ):
                rec.shop_only_quotation = "never"
            elif all(rec.product_variant_ids.mapped("shop_only_quotation")):
                rec.shop_only_quotation = "all_variant"
            elif any(rec.product_variant_ids.mapped("shop_only_quotation")):
                rec.shop_only_quotation = "manually_on_variant"

    def _inverse_shop_only_quotation(self):
        # Sets the value on all its variants
        for rec in self:
            if rec.shop_only_quotation == "all_variant":
                rec.product_variant_ids.shop_only_quotation = True
            elif rec.shop_only_quotation == "never":
                rec.product_variant_ids.shop_only_quotation = False

    def _create_variant_ids(self):
        # Make sure new variants have the same value than the template.
        res = super()._create_variant_ids()
        for rec in self:
            if rec.shop_only_quotation == "all_variant":
                rec.product_variant_ids.shop_only_quotation = True
        return res
