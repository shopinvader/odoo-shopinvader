# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Product Brand",
    "summary": "Shopinvader product Brand",
    "version": "14.0.1.2.0",
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
        "product_brand",
        # To avoid too much glue module we directly depend of shopinvader_search_engine
        # if someone really need this module without the search part please do a PR
        "shopinvader_search_engine",
    ],
    "data": [
        "views/product_brand_view.xml",
        "views/shopinvader_brand_view.xml",
        "views/shopinvader_backend_view.xml",
        "data/ir_export_brand.xml",
        "data/ir_export_product.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
}
