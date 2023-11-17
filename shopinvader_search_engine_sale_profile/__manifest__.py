# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Shopinvader Search Engine Sale Profile",
    "summary": """Sales profiles for Shopinvader""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "category": "e-commerce",
    "author": "Akretion,ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "product_get_price_helper",
        "shopinvader_sale_profile",
        "shopinvader_search_engine",
    ],
    "data": ["views/se_backend.xml"],
    "demo": [],
    "installable": True,
}
