# -*- coding: utf-8 -*-
#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale_cart',
    'version': '8.0.0.1.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': """
    This module allows to have a cart sub state in the sale order.
    """,
    'author': 'Akretion',
    'website': 'http://wwww.akretion.com/',
    'depends': [
        'sale_substate',
        ],
    'data': [
        'views/sale_menu.xml',
        ],
    'demo': [
        'demo/cart_demo.xml',
        ],
    'installable': True,
}
