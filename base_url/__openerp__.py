# -*- coding: utf-8 -*-
##############################################################################
#
#    Rewrite url Base module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
##############################################################################

{
    'name': 'Base Url',
    'version': '8.0.0.1.0',
    'category': 'tools',
    'license': 'AGPL-3',
    'summary': 'keep history of url for product & categorie  ',

    'author': 'Akretion',
    'website': 'https://www.akretion.fr',
    # any module necessary for this one to work correctly
    'depends': [],
    'external_dependencies': {
        'bin': [],
        'python': ['slugify'],
    },
    'data': ['views/url_view.xml',
             'security/ir.model.access.csv'],

    'demo': [],

    'url': '',
    'installable': True,
}
