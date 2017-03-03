# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    type = fields.Selection(selection_add=[('shop', 'Online Shop')])


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shop_categ_id = fields.Many2one(
        'product.category', string='Online Shop Category',
        domain=[('type', '=', 'shop')],
        ondelete='restrict', track_visibility='onchange')
