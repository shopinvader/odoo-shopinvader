# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Shopinvader Assortment',
    'description': """
        This addon allows to assign an assortment to a shopinvader
        backend and get products auto-binded while exported
        to search engine""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'http://acsone.eu',
    'depends': [
        'product_assortment',
        'shopinvader',
        'shopinvader_search_engine',
    ],
    'data': [
        'views/shopinvader_backend.xml',
    ],
    'demo': [
        'demo/shopinvader_assortment_demo.xml'
    ],
}
