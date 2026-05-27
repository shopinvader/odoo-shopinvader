# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Cart Quotation",
    "summary": """Glue module between sale_quotation and sale_cart""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["sale_quotation", "sale_cart"],
    "data": ["views/sale_order.xml", "data/mail_templates.xml"],
    "demo": [],
}
