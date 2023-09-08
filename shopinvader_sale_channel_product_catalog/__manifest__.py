# Copyright 2023 Akretion (http://www.akretion.com)
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Sale Channel Product Catalog",
    "summary": "Glue module",
    "version": "16.0.0.1.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "maintainer": ["hparfr"],
    "depends": [
        "shopinvader_sale_channel",
        "sale_channel_product_catalog",
    ],
    "data": [
        "views/product_catalog.xml",
    ],
}
