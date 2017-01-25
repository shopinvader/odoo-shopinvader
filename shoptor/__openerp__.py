# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shoptor",
    "summary": "Shoptor API",
    "version": "8.0.1.0.0",
    "category": "e-commerce",
    "website": "https://odoo-community.org/",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale_cart",
        "base_jsonify",
        "connector_locomotivecms",
        "base_view_inheritance_extension",
        "connector_base_product",
        "product_multi_image",
        "product_media",
        "product_stock_state",
    ],
    "data": [
        'views/product_view.xml',
        'views/image_view.xml',
        'views/media_view.xml',
        'views/backend_view.xml',
        'views/product_category_view.xml',
        'security/ir.model.access.csv',
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
