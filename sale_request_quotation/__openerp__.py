# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: MonsieurB
#    Copyright 2015 Akretion SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
    'depends': ['sale', 'sale_substate'],
    'data': [],
    'demo': ['quotation_demo.xml'],
    'test': ['tests/test_request_quotations'],
    'installable': True,
}
