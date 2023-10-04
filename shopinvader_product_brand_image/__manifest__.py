# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Product Brand Image",
    "summary": "Shopinvader product Brand Image",
    "version": "16.0.1.0.0",
    "category": "Shopinvader",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "shopinvader_product_brand",
        "shopinvader_search_engine_image",
        "shopinvader_search_engine_product_brand",
        "fs_product_brand_multi_image",
    ],
    "data": [],
    "demo": [],
}
