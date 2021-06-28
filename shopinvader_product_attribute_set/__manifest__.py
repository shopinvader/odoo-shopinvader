# Copyright 2021 Akretion (http://www.akretion.com)
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Product Attribute Set",
    "summary": "Expose all PIM' Attribute sets with Shopinvader",
    "version": "14.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["shopinvader", "product_attribute_set"],
    "data": ["data/ir_export_product.xml", "views/product_filter_view.xml"],
    "demo": ["demo/product_filter.xml"],
}
