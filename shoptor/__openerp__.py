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
        "sale",
        "connector_nosql_product",
        "connector_nosql_locomotivecms",
        "product_url",
    ],
    "data": [
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
