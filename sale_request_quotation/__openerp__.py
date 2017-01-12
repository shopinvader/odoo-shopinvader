# -*- coding: utf-8 -*-
#    Copyright (C) 2016 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale_request_quotation',
    'version': '8.0.0.1.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': """
    This module allows to have a request quotation value in  sub state in
    the sale order.
    """,
    'author': 'Akretion',
    'website': 'http://wwww.akretion.com/',
    'depends': ['sale_substate'],
    'data': [],
    'demo': ['quotation_demo.xml'],
    'test': ['tests/test_request_quotation.py'],
    'installable': True,
}
