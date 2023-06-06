# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopvinvader Product Brand Tag",
    "summary": "Index Product Brand Tags in Shopinvader",
    "version": "14.0.1.0.0",
    "category": "e-Commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "depends": ["shopinvader_product_brand", "product_brand_tag"],
    "data": [
        "data/ir_export_product_brand.xml",
        "data/ir_export_product.xml",
    ],
    "installable": False,
}
