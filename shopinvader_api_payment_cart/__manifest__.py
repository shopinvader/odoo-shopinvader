# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api Payment Cart",
    "summary": """
        Adds logic to be able to pay current cart""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        # Odoo
        "account_payment",
        # Shopinvader
        "fastapi",
        "sale_cart",
        "shopinvader_api_payment",
        "shopinvader_api_cart",
    ],
    "data": [
        "views/payment_provider.xml",
    ],
}
