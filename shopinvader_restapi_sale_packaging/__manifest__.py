# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Restapi Product Sale Packaging",
    "Summary": """
        REST services take care of if products are sold by packagings.
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp SA",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader_restapi",
        "shopinvader_product",
        "shopinvader_product_sale_packaging",
        "sale_stock",
    ],
    "installable": True,
}
