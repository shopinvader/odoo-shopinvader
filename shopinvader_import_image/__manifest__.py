# -*- coding: utf-8 -*-
###############################################################################
#
#    Akretion
#    Copyright (C) 2018-TODAY Akretion (<https://www.cybrosys.com>)
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Saritha Sahadevan (<https://www.cybrosys.com>)
#    Author: Sylvain Calador (<https://www.akretion.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': 'Import Shopinvader product image',
    'version': '10.0.1.0.0',
    'summary': 'Import product images',
    'description': '''
        Import product image from a CVS file from URLs or ZIP file',
    ''',
    'author': 'Sylvain Calador',
    'company': 'Akretion',
    'maintainer': 'Akretion',
    'website': 'https://www.akretion.com',
    'category': 'Product',
    'depends': [
        'shopinvader_image'
    ],
    'data': [
        'views/import_product_image_view.xml'
    ],
    'license': 'AGPL-3',
    'images': [''],
    'application': False,
    'installable': True,
    'auto_install': False,
}
