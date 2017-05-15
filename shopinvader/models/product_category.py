# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


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
    parent = fields.Many2one(
        'shopinvader.category',
        'Shopinvader Parent',
        compute='_compute_parent_category',
        store=True)
    level = fields.Integer(compute='_compute_level')

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id, lang_id)',
         'A category can only have one binding by backend.'),
    ]

    def _should_have_parent(self):
        return bool(self.parent_id)

    @api.depends('parent_id.shopinvader_bind_ids')
    def _compute_parent_category(self):
        for record in self:
            for binding in record.parent_id.shopinvader_bind_ids:
                if binding.backend_id == record.backend_id:
                    record.shopinvader_parent_id = binding.id
                    break
            if not record.parent and record._should_have_parent():
                raise UserError(
                    _('The category must have its parent '
                      'exported into shopinvader'))

    def _build_url_key(self):
        key = super(ShopinvaderCategory, self)._build_url_key()
        if self.parent_id and self.parent:
            # TODO using self.shopinvader_parent_id.url_key fail...
            if self.parent.url_builder == 'manual':
                parent_url = self.parent.manual_url_key
            else:
                parent_url = self.parent._build_url_key()
            key = '/'.join([parent_url, key])
        return key

    @api.depends(
        'url_builder',
        'record_id.name',
        'parent.url_key')
    def _compute_url(self):
        return super(ShopinvaderCategory, self)._compute_url()

    @api.depends('parent.level')
    def _compute_level(self):
        for record in self:
            record.level = 0
            parent = record.parent
            while parent:
                record.level += 1
                parent = parent.parent

    def _compute_image(self):
        for record in self:
            images = []
            # TODO get image from public storage
            record.images = images
