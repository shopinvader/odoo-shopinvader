# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Cart steps",
    "summary": """
    Track checkout steps on sale cart.
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["sale_cart"],
    "data": [
        "data/cart_step.xml",
        "security/ir.model.access.csv",
        "views/sale_order.xml",
        "views/cart_step.xml",
    ],
}
