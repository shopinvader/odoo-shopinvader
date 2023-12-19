# Copyright 2020 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Product Sale Packaging",
    "Summary": """
        Sell products by packaging.
    """,
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "Camptocamp SA",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "extendable_fastapi",
        "shopinvader_product",
        "sale_stock",
        "sell_only_by_packaging",
        "stock_packaging_calculator_packaging_level",
    ],
    "data": [
        "views/product_packaging.xml",
        "views/product_packaging_level.xml",
    ],
    "installable": True,
}
