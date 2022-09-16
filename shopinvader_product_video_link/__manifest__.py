# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Product Video Link",
    "summary": "Add video on your Shopinvader website",
    "version": "14.0.1.0.2",
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
        "shopinvader",
        "product_video_link",
    ],
    "data": [
        "data/ir_export_product.xml",
        "data/ir_export_category.xml",
    ],
    "demo": [],
}
