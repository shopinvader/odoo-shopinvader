# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Locomotive CMS Connector',
    'version': '10.0.0.0.1',
    'category': 'Connector',
    'summary': 'Connector For Locomotive CMS',
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'images': [],
    'depends': [
        'connector',
        'keychain',
    ],
    'data': [
        'views/locomotive_view.xml',
        'views/locomotive_menu.xml',
        'security/ir.model.access.csv',
        'security/locomotive_backend_security.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'external_dependencies': {
        'python': ['locomotivecms'],
        },
    'installable': True,
    'auto_install': False,
    'application': False,
}
