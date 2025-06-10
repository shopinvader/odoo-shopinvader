# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    shop_order_mode = fields.Selection(
        selection=[("direct_sale_only", _("Direct Sale Only"))],
        string="Shopinvader Order Mode",
        default="direct_sale_only",
        help="Deault order mode for this template's products in Shopinvader.",
    )

    is_shop_order_mode_enabled_on_variant = fields.Boolean(
        string="Shopinvader Order Mode Unabled on Variant",
        help="If True, unables product variants to have a different value for"
        " 'shop_order_mode' than this product template.",
        default=False,
    )
