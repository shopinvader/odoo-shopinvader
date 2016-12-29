# -*- coding: utf-8 -*-
#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'product_url',
    'version': '8.0.0.1.0',
    'category': 'tools',
    'license': 'AGPL-3',
    'summary': 'keep history of url for products & categories  ',

    'author': 'Akretion',
    'website': 'http://www.akretion.com/fr',
    'depends': ['product', 'base_url'],

    'data': ['views/product_view.xml',
             'views/category_view.xml', ],

    'demo': ['demo/url.url.csv'],

    'url': '',
    'installable': True,
    'auto_install': False,
    'application': False,
}
