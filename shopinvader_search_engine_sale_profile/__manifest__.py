# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'ShopInvader search engine - Sale profile',
    'description': """
        This ShopInvader search engine submodule used to define a price on the
        shopinvader variant (depending on the sale profile)""",
    'version': '10.0.1.0.0',
    'depends': [
        'shopinvader_sale_profile',
        'shopinvader_search_engine',
    ],
    'author': 'ACSONE SA/NV',
    'website': 'http://www.acsone.eu',
    'license': 'AGPL-3',
    'category': 'e-commerce',
    'installable': True,
    'auto_install': True,
}
