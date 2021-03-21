# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Quotation",
    "summary": "Shopinvader Quotation",
    "version": "10.0.1.1.0",
    "category": "e-commerce",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "author": "Akretion",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["shopinvader"],
    "demo": ["demo/email_demo.xml", "demo/notification_demo.xml"],
    "data": [
        "views/product_view.xml",
        "views/sale_view.xml",
        "data/ir_export_product.xml",
    ],
}
