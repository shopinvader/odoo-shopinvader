# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Payment",
    "summary": "Payment integration for Shopinvader",
    "version": "10.0.1.0.0",
    "category": "e-commerce",
    "website": "https://akretion.com",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": True,
    'installable': True,
    "external_dependencies": {
        "python": ['cerberus', 'unidecode'],
        "bin": [],
    },
    "depends": [
        "shopinvader",
        "payment_gateway",
    ],
    "data": [
        'views/shopinvader_payment_view.xml',
        'views/backend_view.xml',
    ],
    "demo": [
        # "demo/payment_demo.xml",
    ],
    "qweb": [
    ]
}
