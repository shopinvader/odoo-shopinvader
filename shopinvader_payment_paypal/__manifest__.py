# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shopinvader Payment Paypal",
    "summary": "Shopinvader Paypal Payment Gateway",
    "version": "10.0.1.0.0",
    "category": "e-commerce",
    "website": "https://akretion.com",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": False,
    'installable': True,
    "auto_install": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "shopinvader_payment",
        "payment_gateway_paypal",
    ],
    "data": [
    ],
    "demo": [
        "demo/shopinvader_payment_demo.xml",
    ],
    "qweb": [
    ]
}
