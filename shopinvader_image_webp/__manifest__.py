# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader image WebP",
    "summary": """Shopinvader WebP module""",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "category": "shopinvader",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["shopinvader_image"],
    "external_dependencies": {"python": ["Pillow"]},
    "data": ["data/ir_export_product.xml", "data/ir_export_category.xml"],
    "installable": True,
}
