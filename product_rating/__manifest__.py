# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Rating',
    'version': '10.0.1.0.0',
    'author': "Akretion",
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Uncategorized',
    'summary': 'Rate your product',
    'depends': [
        'sales_team',
        'product'
    ],
    'data': [
        'views/product_rating_view.xml',
        'views/product_view.xml',
        'data/product_rating_data.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
