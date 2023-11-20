# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Product Brand",
    "summary": "Shopinvader product Brand",
    "version": "16.0.1.0.1",
    "category": "Shopinvader",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        # OCA
        "product_brand",
        # Shopinvader
        "shopinvader_base_url",
        "shopinvader_product",
        "shopinvader_product_seo",
    ],
    "data": [
        "views/product_brand_view.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["extendable_pydantic>=1.2.0"]},
    "development_status": "Alpha",
}
