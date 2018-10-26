# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderProduct(models.Model):
    _name = 'shopinvader.product'
    _description = 'Shopinvader Product'
    _inherit = ['shopinvader.binding', 'abstract.url']
    _inherits = {'product.template': 'record_id'}

    record_id = fields.Many2one(
        'product.template',
        required=True,
        ondelete='cascade',
        index=True,
    )
    seo_title = fields.Char()
    meta_description = fields.Char()
    meta_keywords = fields.Char()
    short_description = fields.Html()
    description = fields.Html()
    shopinvader_variant_ids = fields.One2many(
        'shopinvader.variant',
        'shopinvader_product_id',
        'Shopinvader Variant')
    active = fields.Boolean(
        default=True,
        inverse='_inverse_active')
    url_key = fields.Char(
        compute_sudo=True,
    )
    use_product_shopinvader_name = fields.Boolean(
        related='backend_id.use_product_shopinvader_name',
        store=True, readonly=True)
    shopinvader_name = fields.Char(
        string='Name',
        help="Name for shopinvader, if not set the product name will be used.")
    model_name = fields.Char(compute='_compute_name', readonly=True)

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id, lang_id)',
         'A product can only have one binding by backend and lang.'),
    ]

    @api.depends('use_product_shopinvader_name', 'shopinvader_name')
    def _compute_name(self):
        for record in self:
            if record.use_product_shopinvader_name and record.shopinvader_name:
                record.model_name = record.shopinvader_name
            else:
                record.model_name = record.name

    @api.multi
    def _inverse_active(self):
        self.filtered(
            lambda p: not p.active).mapped('shopinvader_variant_ids').write(
                {'active': False})

    def _prepare_shopinvader_variant(self, variant):
        values = {
            'record_id': variant.id,
            'shopinvader_product_id': self.id,
        }
        # If the variant is not active, we have to force active = False
        if not variant.active:
            values.update({
                'active': variant.active,
            })
        return values

    def _create_shopinvader_variant(self):
        """
        Create missing shopinvader.variant and return new just created
        :return: shopinvader.variant recordset
        """
        self.ensure_one()
        self_ctx = self.with_context(active_test=False)
        shopinv_variant_obj = self_ctx.env['shopinvader.variant']
        shopinv_variants = shopinv_variant_obj.browse()
        for variant in self_ctx.product_variant_ids:
            if not shopinv_variant_obj.search_count([
                ('record_id', '=', variant.id),
                ('shopinvader_product_id', '=', self.id),
            ]):
                vals = self_ctx._prepare_shopinvader_variant(variant)
                shopinv_variants |= shopinv_variant_obj.create(vals)
        return shopinv_variants

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
            backend = self.env['shopinvader.backend'].search([], limit=1)
            res['backend_id'] = backend.id
        return res

    @api.multi
    def toggle_published(self):
        """
        Toggle the active field
        :return: dict
        """
        actual_active = self.filtered(
            lambda s: s.active).with_prefetch(self._prefetch)
        actual_inactive = self - actual_active
        actual_inactive = actual_inactive.with_prefetch(self._prefetch)
        if actual_inactive:
            actual_inactive.write({
                'active': True,
            })
        if actual_active:
            actual_active.write({
                'active': False,
            })
        return {}
