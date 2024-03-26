# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api Payment Provider SIPS",
    "summary": """
        Specific routes for SIPS payments from Shopinvader""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "fastapi",
        "shopinvader_api_payment",
        "payment_sips",
    ],
    "data": [],
    "demo": [],
}
