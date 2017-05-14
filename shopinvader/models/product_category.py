# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = [_name, "base_multi_image.owner"]

    shopinvader_bind_ids = fields.One2many(
        'shopinvader.category',
        'record_id',
        string='Shopinvader Binding')
    filter_ids = fields.Many2many(
        comodel_name='product.filter',
        string='Filter')


class ShopinvaderCategory(models.Model):
    _name = 'shopinvader.category'
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
    meta_keywords = fields.Char()
    subtitle = fields.Char()
    short_description = fields.Html()
    description = fields.Html()
    images = fields.Serialized(
        compute='_compute_image',
        string='Shopinvader Image')

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id, lang_id)',
         'A category can only have one binding by backend.'),
    ]

    @api.depends('url_builder', 'record_id.name')
    def _compute_url(self):
        return super(ShopinvaderCategory, self)._compute_url()

    def _compute_image(self):
        for record in self:
            images = []
            # TODO get image from public storage
            record.images = images
