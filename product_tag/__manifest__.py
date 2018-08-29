# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Tag',
    'version': '10.0.1.0.0',
    'author': "Akretion",
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'category': 'E-commerce',
    'summary': 'Tag your product',
    'depends': [
        'product',
        'sales_team'
    ],
    'data': [
        'views/product_tag_view.xml',
        'views/product_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
