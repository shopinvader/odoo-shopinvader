# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# Copyright 2016 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Invader',
    'description': """
        Base module to build secured REST services""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Akretion, ACSONE SA/NV',
    'website': 'https://akretion.com',
    'depends': [
        'component',
    ],
    'external_dependencies': {
        'python': [
            'cerberus',
            'unidecode'
        ],
    },
    'data': [
        'security/base_invader_security.xml',
        'security/invader_entrypoint.xml',
        'views/invader_entrypoint.xml',
    ],
    'demo': [
    ],
}
