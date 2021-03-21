# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Product New",
    "summary": "Shopinvader product new",
    "version": "10.0.0.0.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {},
    "depends": ["shopinvader"],
    "data": [
        "views/product_template.xml",
        "data/ir_export_product.xml",
        "data/ir_cron.xml",
    ],
    "demo": [],
    "qweb": [],
}
