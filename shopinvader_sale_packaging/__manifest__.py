# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Packaging",
    "Summary": """
        Sell products by packaging.
    """,
    "version": "13.0.2.1.1",
    "license": "AGPL-3",
    "author": "Camptocamp SA",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader",
        "sale_stock",
        "sale_by_packaging",
        "stock_packaging_calculator",
    ],
    "data": ["data/ir_export_product.xml"],
}
