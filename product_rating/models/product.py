# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    rating_ids = fields.One2many(
        'product.rating',
        'product_tmpl_id',
        'Rating')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    rating_ids = fields.One2many(
        'product.rating',
        'product_tmpl_id',
        'Rating')
