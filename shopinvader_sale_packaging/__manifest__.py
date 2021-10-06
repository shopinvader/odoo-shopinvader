# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Packaging",
    "Summary": """
        Sell products by packaging.
    """,
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp SA",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader",
        "sale_stock",
        "sale_by_packaging",
        "stock_packaging_calculator_packaging_type",
    ],
    "data": ["data/ir_export_product.xml"],
    "installable": False,
}
