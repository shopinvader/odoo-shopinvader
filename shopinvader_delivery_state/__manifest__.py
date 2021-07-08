# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader delivery state",
    "Summary": """
        Integrate `sale_delivery_state` with Shopinvader
    """,
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp SA",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["shopinvader", "sale_delivery_state"],
    "auto_install": True,
    "post_init_hook": "post_init_hook",
}
