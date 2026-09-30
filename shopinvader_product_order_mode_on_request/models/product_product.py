# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    shop_order_mode = fields.Selection(
        selection_add=[
            ("quotation_only", "Quotation Only"),
            ("direct_sale_or_quotation", "Direct Sale or Quotation"),
        ],
        ondelete={
            "quotation_only": "set null",
            "direct_sale_or_quotation": "set null",
        },
    )
