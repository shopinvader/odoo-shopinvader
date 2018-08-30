# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Shopinvader Product Rating',
    'version': '10.0.1.0.0',
    'author': "Akretion",
    'website': 'https://akretion.com',
    'license': 'AGPL-3',
    'category': 'e-commerce',
    'summary': 'Shopinvader Product Rating',
    'depends': [
        'shopinvader',
        'product_rating',
    ],
    'data': [
        'data/ir_export.xml',
    ],
    'installable': True,
    'auto_install': True,
}
