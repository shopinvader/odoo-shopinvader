# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api Payment",
    "summary": """
        Shopinvader services to be able to pay (invoices, carts,...)""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "fastapi",
        "payment",
        "payment_sips",
        "pydantic",
        "extendable",
        "extendable_fastapi",
    ],
    "data": [],
    "demo": [],
}
