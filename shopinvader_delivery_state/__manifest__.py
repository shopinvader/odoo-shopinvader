# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader delivery state",
    "Summary": """
        Integrate `sale_delivery_state` with Shopinvader
    """,
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "Camptocamp SA",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["shopinvader_sale_state", "sale_delivery_state"],
    "auto_install": True,
    "post_init_hook": "post_init_hook",
    "installable": True,
}
