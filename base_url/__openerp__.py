# -*- coding: utf-8 -*-

##############################################################################
#
#    Rewrite url Base module for OpenERP
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
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
    'name': 'base_url',
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
    'data': ['views/url_view.xml'],

    'demo': [],

    'url': '',
    'installable': True,
    'auto_install': False,
    'application': False,
}
