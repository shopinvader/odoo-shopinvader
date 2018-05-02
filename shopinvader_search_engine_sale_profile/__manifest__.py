# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
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
    'author': 'Akretion,ACSONE SA/NV',
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'category': 'e-commerce',
    'installable': True,
    'auto_install': True,
}
