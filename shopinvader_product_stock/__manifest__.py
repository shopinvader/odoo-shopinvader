# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shopinvader Product Stock",
    "summary": "This module is used to choose a stock field during the"
               "export (by backend)",
    'description': """
        Connector search engine for Stock""",
    "version": "10.0.1.0.0",
    "category": "e-commerce",
    "website": "https://akretion.com",
    "author": "Akretion,ACSONE SA/NV",
    "license": "AGPL-3",
    'installable': True,
    "depends": [
        'stock',
        'shopinvader',
        'queue_job',
        'connector_search_engine',
        'shopinvader_search_engine',
    ],
    "data": [
        'views/se_backend.xml',
    ],
    'external_dependencies': {
        'python': [
            'openupgradelib',
        ],
    },
    'pre_init_hook': 'rename_module',
}
