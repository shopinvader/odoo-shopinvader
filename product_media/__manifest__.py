# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Media',
    'version': '10.0.1.0.0',
    'author': "Akretion, "
              "Serpent Consulting Services Pvt. Ltd.",
    'website': 'http://www.akretion.com',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Give the posibility to store media data on product',
    'depends': [
        'product',
        'storage_image',
    ],
    'data': [
        'views/product_view.xml',
        'data/ir_parameter.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
