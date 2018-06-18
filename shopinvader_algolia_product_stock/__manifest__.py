# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Connector Search Engine Algolia Product stock",
    "summary": "This module is used to apply features of shopinvader_stock"
               "with shopinvader_algolia",
    'description': """
        Connector search engine for Algolia Stock""",
    "version": "10.0.1.0.0",
    "category": "e-commerce",
    "website": "https://akretion.com",
    "author": "Akretion,ACSONE SA/NV",
    "license": "AGPL-3",
    "depends": [
        'stock',
        'shopinvader',
        'connector_search_engine',
        'shopinvader_product_stock',
        'shopinvader_algolia',
    ],
    "data": [
        'views/se_backend_algolia.xml',
    ],
    'external_dependencies': {
        'python': [
            'openupgradelib',
        ],
    },
    'pre_init_hook': 'pre_init_hook',
}
