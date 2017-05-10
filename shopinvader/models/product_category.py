# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = [_name, "base_multi_image.owner"]

    locomotive_bind_ids = fields.One2many(
        'locomotive.category',
        'record_id',
        string='Locomotive Binding')
    filter_ids = fields.Many2many(
        comodel_name='product.filter',
        string='Filter')


class LocomotiveCategory(models.Model):
    _name = 'locomotive.category'
    _inherit = ['locomotive.binding', 'abstract.url']
    _inherits = {'product.category': 'record_id'}

    record_id = fields.Many2one(
        'product.category',
        required=True,
        ondelete='cascade')
    lang_id = fields.Many2one(
        'res.lang',
        'Lang',
        required=True)
    seo_title = fields.Char()
    meta_description = fields.Char()
    meta_keyword = fields.Char()
    subtitle = fields.Char()
    link_label = fields.Char()
    short_description = fields.Html()
    description = fields.Html()

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id, lang_id)',
         'A category can only have one binding by backend.'),
    ]

    @api.depends('url_builder', 'record_id.name')
    def _compute_url(self):
        return super(LocomotiveCategory, self)._compute_url()
