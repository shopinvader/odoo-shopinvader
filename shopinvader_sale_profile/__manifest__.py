# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'ShopInvader - Sale profile',
    'description': """
        This ShopInvader submodule give the possibility to specify some
        sale profiles (with pricelist per profile) per backend to apply on
        your customers""",
    'version': '10.0.1.0.0',
    'depends': [
        'base',
        'connector_locomotivecms',
        'shopinvader',
    ],
    'author': 'ACSONE SA/NV',
    'website': 'http://www.acsone.eu',
    'license': 'AGPL-3',
    'category': 'e-commerce',
    'data': [
        'views/locomotive_backend.xml',
        'views/res_partner.xml',
        'views/shopinvader_partner.xml',
        'security/shopinvader_sale_profile.xml',
    ],
    'demo': [
        'demo/shopinvader_sale_profile.xml',
    ],
    'installable': True,
}
