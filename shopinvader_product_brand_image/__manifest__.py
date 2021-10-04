# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Product Brand Image",
    "summary": "Shopinvader product Brand Image",
    "version": "14.0.1.0.0",
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
        "shopinvader_image",
        "storage_image_product_brand",
    ],
    "data": [
        "data/ir_export_brand.xml",
        "views/shopinvader_backend_view.xml",
    ],
    "demo": [
        "demo/backend_demo.xml",
    ],
}
