# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader price visible discount",
    "summary": "Shopinvader show pricelist discount on your e-commerce shop",
    "version": "8.0.1.0.0",
    "category": "e-commerce",
    "website": "https://akretion.com",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "shopinvader",
        "product_visible_discount",
    ],
    "data": [
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
