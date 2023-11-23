# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Search Engine Assortment",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": [
        "product_assortment",
        "shopinvader_product",
        "shopinvader_search_engine",
    ],
    "data": ["data/ir_cron.xml", "views/se_backend.xml"],
    "demo": ["demo/shopinvader_assortment_demo.xml"],
}
