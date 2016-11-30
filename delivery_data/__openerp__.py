# -*- coding: utf-8 -*-
#    Rewrite url Base module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Delivery data',
    'version': '8.0.0.1.0',
    'category': 'tools',
    'license': 'AGPL-3',
    'summary': 'dev data integration for delivery  ',

    'author': 'Akretion',
    'website': 'http://www.akretion.com/fr',
    # any module necessary for this one to work correctly
    'depends': ['delivery'],

    'data': ['delivery_la_poste.xml',
             'delivery_om1.xml',
             'delivery_om2.xml',
             'delivery_inter_z1.xml',
             'delivery_inter_z2.xml',
             'delivery_inter_z3.xml',
             'delivery_inter_z4.xml',
             'delivery_inter_z5.xml',
             'delivery_inter_z6.xml',
             'delivery_inter_z7.xml',
             'delivery_inter_z8.xml',
             'delivery_from_factory.xml',
             'delivery_tnt_24h.xml',
             'delivery.grid.csv',
              ],

    'demo': [],

    'url': '',
    'installable': True,
}
