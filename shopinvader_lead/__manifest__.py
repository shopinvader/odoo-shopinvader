# -*- coding: utf-8 -*-

{
    "name": "Shopinvader Lead",
    "summary": "Shopinvader Lead Management",
    "version": "10.0.1.0.0",
    "category": "e-commerce",
    "website": "https://akretion.com",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": False,
    'installable': True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "shopinvader",
        "crm",
    ],
    "data": [
    ],
    "demo": [
        'demo/email_demo.xml',
        'demo/notification_demo.xml',
    ],
    "qweb": [
    ]
}
