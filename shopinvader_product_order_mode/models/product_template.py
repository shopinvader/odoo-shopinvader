# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    shop_order_mode = fields.Selection(
        selection=[("direct_sale_only", _("Direct Sale Only"))],
        string="Shopinvader Order Mode",
        default="direct_sale_only",
        help="Deault order mode for this template's products in Shopinvader.",
    )

    is_shop_order_mode_unabled_on_variant = fields.Boolean(
        string="Shopinvader Order Mode Unabled on Variant",
        help="If True, unables product variants to have a different value for"
        " 'shop_order_mode' than this product template.",
        default=False,
    )

    # if product order mode goes from unabled to disabled on variants, put back all variants
    # to the value of the template
    @api.model
    def write(self, vals):
        res = super().write(vals)
        if (
            "is_shop_order_mode_unabled_on_variant" in vals
            and not vals["is_shop_order_mode_unabled_on_variant"]
        ):
            for template in self:
                template.with_context(
                    skip_shop_order_mode_validation=True
                ).product_variant_ids.write(
                    {"shop_order_mode": template.shop_order_mode}
                )
        return res
