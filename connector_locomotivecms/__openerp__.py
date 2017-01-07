# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Locomotive CMS Connector',
    'version': '8.0.0.0.1',
    'category': 'Connector',
    'summary': 'Connector For Locomotive CMS',
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'images': [],
    'depends': [
        'connector_generic',
    ],
    'data': [
        'views/locomotive_view.xml',
        'views/locomotive_menu.xml',
    ],
    'demo': [
        'demo/backend_demo.xml',
    ],
    'test': [
    ],
    'external_dependencies': {
        'python': [],
        },
    'installable': True,
    'auto_install': False,
    'application': False,
}
