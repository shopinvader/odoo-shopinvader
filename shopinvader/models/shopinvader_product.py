# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderProduct(models.Model):
    _name = 'shopinvader.product'
    _description = 'Shopinvader Product'
    _inherit = ['locomotive.binding', 'abstract.url']
    _inherits = {'product.template': 'record_id'}

    record_id = fields.Many2one(
        'product.template',
        required=True,
        ondelete='cascade')
    seo_title = fields.Char()
    meta_description = fields.Char()
    meta_keywords = fields.Char()
    shopinvader_variant_ids = fields.One2many(
        'shopinvader.variant',
        'shopinvader_product_id',
        'Shopinvader Variant')
    active = fields.Boolean(
        default=True,
        inverse='_inverse_active')

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id)',
         'A product can only have one binding by backend.'),
    ]

    @api.multi
    def _inverse_active(self):
        inactive = self.filtered(lambda p: not p.active)
        inactive.shopinvader_variant_ids.write(
            {'active': False})

    def _prepare_shopinvader_variant(self, variant):
        return {
            'record_id': variant.id,
            'shopinvader_product_id': self.id,
            }

    def _create_shopinvader_variant(self):
        self.ensure_one()
        for variant in self.product_variant_ids:
            if not self.env['shopinvader.variant'].search([
                    ('record_id', '=', variant.id),
                    ('shopinvader_product_id', '=', self.id),
                    ]):
                vals = self._prepare_shopinvader_variant(variant)
                self.env['shopinvader.variant'].create(vals)

    @api.model
    def create(self, vals):
        binding = super(ShopinvaderProduct, self).create(vals)
        if self.env.context.get('map_children'):
            binding._create_shopinvader_variant()
        return binding

    def _build_url_key(self):
        key = super(ShopinvaderProduct, self)._build_url_key()
        if self.default_code:
            key = '-'.join([key, self.default_code])
        return key

    @api.depends('url_builder', 'record_id.name')
    def _compute_url(self):
        return super(ShopinvaderProduct, self)._compute_url()

    @api.model
    def default_get(self, fields_list):
        res = super(ShopinvaderProduct, self).default_get(fields_list)
        if 'backend_id' in fields_list:
            backend = self.env['locomotive.backend'].search([], limit=1)
            res['backend_id'] = backend.id
        return res
