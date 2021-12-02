# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Shopinvader Product Manufactured For",
    "summary": "Manage Product Made Specially For Some Customers",
    "version": "14.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["shopinvader", "product_sale_manufactured_for"],
    "data": ["data/ir_export_product.xml"],
    "auto_install": True,
}
