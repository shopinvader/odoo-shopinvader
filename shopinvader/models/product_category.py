# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = [_name, "storage.image.owner"]

    shopinvader_bind_ids = fields.One2many(
        'shopinvader.category',
        'record_id',
        string='Shopinvader Binding')
    filter_ids = fields.Many2many(
        comodel_name='product.filter',
        string='Filter')


class ShopinvaderCategory(models.Model):
    _name = 'shopinvader.category'
    _description = 'Shopinvader Category'
    _inherit = ['locomotive.binding', 'abstract.url']
    _inherits = {'product.category': 'record_id'}

    record_id = fields.Many2one(
        'product.category',
        required=True,
        ondelete='cascade')
    object_id = fields.Integer(
        compute='_compute_object_id',
        store=True)
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
    shopinvader_parent_id = fields.Many2one(
        'shopinvader.category',
        'Shopinvader Parent',
        compute='_compute_parent_category',
        store=True)
    shopinvader_child_ids = fields.Many2many(
        'shopinvader.category',
        'Shopinvader Childs',
        compute='_compute_child_category')
    level = fields.Integer(compute='_compute_level')
    redirect_url_key = fields.Serialized(
        compute='_compute_redirect_url_key',
        string='Redirect Url Keys')

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id, lang_id)',
         'A category can only have one binding by backend.'),
    ]

    def _compute_redirect_url_key(self):
        for record in self:
            res = []
            for url in record.redirect_url_key_ids:
                res.append(url.url_key)
            record.redirect_url_key = res

    def _compute_image(self):
        for record in self:
            images = []
            for image in record.record_id.image_ids:
                res = {'original': image.url}
                for resize in record.backend_id.categ_image_resize_ids:
                    res[resize.key] = \
                        image.get_thumbnail_from_resize(resize).url
                images.append(res)
            record.images = images

    @api.depends('record_id')
    def _compute_object_id(self):
        for record in self:
            record.object_id = record.record_id.id

    @api.depends('parent_id.shopinvader_bind_ids')
    def _compute_parent_category(self):
        for record in self:
            for binding in record.parent_id.shopinvader_bind_ids:
                if binding.backend_id == record.backend_id:
                    record.shopinvader_parent_id = binding
                    break

    def _compute_child_category(self):
        for record in self:
            record.shopinvader_child_ids = self.search([
                ('record_id.parent_id', '=', record.record_id.id),
                ('backend_id', '=', record.backend_id.id),
                ])

    def _build_url_key(self):
        key = super(ShopinvaderCategory, self)._build_url_key()
        if self.parent_id and self.shopinvader_parent_id:
            # TODO using self.shopinvader_parent_id.url_key fail...
            if self.shopinvader_parent_id.url_builder == 'manual':
                parent_url = self.shopinvader_parent_id.manual_url_key
            else:
                parent_url = self.shopinvader_parent_id._build_url_key()
            key = '/'.join([parent_url, key])
        return key

    @api.depends(
        'url_builder',
        'record_id.name',
        'shopinvader_parent_id.url_key')
    def _compute_url(self):
        return super(ShopinvaderCategory, self)._compute_url()

    @api.depends('shopinvader_parent_id.level')
    def _compute_level(self):
        for record in self:
            record.level = 0
            parent = record.shopinvader_parent_id
            while parent:
                record.level += 1
                parent = parent.shopinvader_parent_id
