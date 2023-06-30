# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Product Pack",
    "summary": """Integrate Product Pack on Shopinvader""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L.",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["shopinvader", "sale_product_pack"],
    "data": ["data/ir_export_product.xml"],
    "application": False,
    "installable": True,
}
