# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

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
