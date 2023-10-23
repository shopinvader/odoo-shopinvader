# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Search Engine Product Seo",
    "summary": """
        This module allows to configure a seo title suffix on se backends""",
    "version": "16.0.1.0.0",
    "category": "Shopinvader",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "ACSONE SA/NV",
    "license": "AGPL-3",
    "depends": ["shopinvader_product_seo", "shopinvader_search_engine"],
    "data": ["views/se_backend.xml"],
    "installable": True,
    "development_status": "Alpha",
}
