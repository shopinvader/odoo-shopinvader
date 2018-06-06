# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Custom Attribute",
    "summary": "Integrate your custom attribute in your website",
    "version": "10.0.1.0.0",
    "category": "e-commerce",
    "website": "https://akretion.com",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": True,
    'installable': True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "shopinvader",
        "product_custom_attributes",
    ],
    "data": [
        "data/ir_export_product.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
