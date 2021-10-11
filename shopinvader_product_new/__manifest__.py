# Copyright 2018 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Product New",
    "summary": "Shopinvader product new",
    "version": "14.0.1.0.1",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["shopinvader"],
    "data": [
        "views/product_template.xml",
        "data/ir_export_product.xml",
        "data/ir_cron.xml",
    ],
}
