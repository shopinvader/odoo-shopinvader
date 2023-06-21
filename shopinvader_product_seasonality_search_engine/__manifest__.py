# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Product Seasonality Search Engine",
    "Summary": """
        Glue module for shopinvader_product_seasonality and search engine.
    """,
    "version": "14.0.1.0.1",
    "license": "AGPL-3",
    "author": "Camptocamp SA",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "shopinvader_product_seasonality",
        "shopinvader_search_engine",
    ],
    "data": [
        "views/shopinvader_seasonal_config.xml",
    ],
    "installable": True,
    "auto_install": True,
}
