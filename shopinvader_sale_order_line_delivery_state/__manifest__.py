# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Order Line Delivery State",
    "Summary": """
        Integrate `sale_order_line_delivery_state` with Shopinvader
    """,
    "version": "13.0.1.0.1",
    "license": "AGPL-3",
    "author": "ForgeFlow",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["shopinvader", "sale_order_line_delivery_state"],
    "auto_install": True,
    "post_init_hook": "post_init_hook",
}
