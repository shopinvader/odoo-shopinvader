# Copyright 2023 Akretion (http://www.akretion.com)
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Sale Channel",
    "summary": "Glue module",
    "version": "16.0.0.1.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "maintainer": ["hparfr"],
    "depends": [
        "shopinvader",
        "sale_channel",
    ],
    "data": [
        "views/shopinvader_backend.xml",
        "views/sale_channel.xml",
    ],
}
