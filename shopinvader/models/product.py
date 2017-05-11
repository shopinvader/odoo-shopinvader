# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp import SUPERUSER_ID


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopinvader_bind_ids = fields.One2many(
        'shopinvader.product',
        'record_id',
        string='Shopinvader Binding')

    @api.multi
    def unlink(self):
        for record in self:
            # TODO we should propose to redirect the old url
            record.shopinvader_bind_ids.unlink()
        return super(ProductTemplate, self).unlink()


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_untaxed_price(self, price):
        if self._uid == SUPERUSER_ID and self._context.get('company_id'):
            taxes = self.taxes_id.filtered(
                lambda r: r.company_id.id == self._context['company_id'])
        else:
            taxes = self.taxes_id
        return self.env['account.tax']._fix_tax_included_price(
            price, taxes, [])

    def _get_rounded_price(self, pricelist, qty, tax_included):
        price = pricelist.price_get(self.id, qty, None)[pricelist.id]
        if not tax_included:
            price = self._get_untaxed_price(price)
        return pricelist.currency_id.round(price)

    def _get_pricelist_dict(self, pricelist, tax_included):
        def get_all_parent(categ):
            if categ:
                return [categ.id] + get_all_parent(categ.parent_id)
            else:
                return []
        self.ensure_one()
        res = []
        categ_ids = get_all_parent(self.categ_id)
        items = self.env['product.pricelist.item'].search([
            '|', '|',
            ('product_id', '=', self.id),
            ('product_tmpl_id', '=', self.product_tmpl_id.id),
            ('categ_id', 'in', categ_ids),
            ])
        item_qty = set([item.min_quantity
                        for item in items if item.min_quantity > 1] + [1])
        last_price = None
        for qty in item_qty:
            price = self._get_rounded_price(pricelist, qty, tax_included)
            if price != last_price:
                res.append({
                    'qty': qty,
                    'price': price,
                    })
                last_price = price
        return res


class ProductFilter(models.Model):
    _name = 'product.filter'
    _description = 'Product Filter'

    field_id = fields.Many2one(
        'ir.model.fields',
        'Field',
        domain=[('model', 'in', (
            'product.template',
            'product.product',
            'shopinvader.product',
            ))])
    help = fields.Html(translate=True)
    name = fields.Char(translate=True, required=True)


class ShopinvaderProduct(models.Model):
    _name = 'shopinvader.product'
    _inherit = ['locomotive.binding', 'abstract.url']
    _inherits = {'product.template': 'record_id'}

    record_id = fields.Many2one(
        'product.template',
        required=True,
        ondelete='cascade')
    lang_id = fields.Many2one(
        'res.lang',
        'Lang',
        required=True)
    seo_title = fields.Char()
    meta_description = fields.Char()
    meta_keywords = fields.Char()
    shopinvader_variant_ids = fields.One2many(
        'shopinvader.variant',
        'shopinvader_product_id',
        'Shopinvader Variant')

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id)',
         'A product can only have one binding by backend.'),
    ]

    def _prepare_shopinvader_variant(self, variant):
        return {
            'record_id': variant.id,
            'shopinvader_product_id': self.id,
            }

    def _create_shopinvader_variant(self):
        self.ensure_one()
        for variant in self.product_variant_ids:
            vals = self._prepare_shopinvader_variant(variant)
            self.env['shopinvader.variant'].create(vals)

    @api.model
    def create(self, vals):
        binding = super(ShopinvaderProduct, self).create(vals)
        binding._create_shopinvader_variant()
        return binding

    @api.depends('url_builder', 'record_id.name')
    def _compute_url(self):
        return super(ShopinvaderProduct, self)._compute_url()

    @api.onchange('backend_id')
    def set_default_lang(self):
        self.ensure_one()
        langs = self.backend_id.lang_ids
        if langs:
            self.lang_id = langs[0]
            return {'domain': {'lang_id': [('id', 'in', langs.ids)]}}

    @api.model
    def default_get(self, fields_list):
        res = super(ShopinvaderProduct, self).default_get(fields_list)
        if 'backend_id' in fields_list:
            backend = self.env['locomotive.backend'].search([], limit=1)
            res['backend_id'] = backend.id
            if backend and backend.lang_ids and 'lang_id' in fields_list:
                res['lang_id'] = backend.lang_ids[0].id
        return res


class ShopinvaderVariant(models.Model):
    _name = 'shopinvader.variant'
    _inherits = {
        'shopinvader.product': 'shopinvader_product_id',
        'product.product': 'record_id'}

    shopinvader_product_id = fields.Many2one(
        'shopinvader.product',
        required=True,
        ondelete='cascade')
    record_id = fields.Many2one(
        'product.product',
        required=True,
        ondelete='cascade')

    # TODO some field are related to the template
    # stock_state
    # images
    # from price / best discount

    categories = fields.Many2many(
        comodel_name='shopinvader.category',
        compute='_compute_categories',
        string='Shopinvader Categories')

    images = fields.Serialized(
        compute='_compute_image',
        string='Shopinvader Image')

    def _get_categories(self):
        self.ensure_one()
        return self.categ_id

    @api.depends('categ_id.shopinvader_bind_ids')
    def _compute_categories(self):
        for record in self:
            shop_categs = []
            for categ in record._get_categories():
                for loco_categ in categ.shopinvader_bind_ids:
                    if loco_categ.backend_id == record.backend_id:
                        shop_categs.append(loco_categ.id)
                        break
            record.categories = shop_categs

    def _compute_image(self):
        for record in self:
            images = []
            # TODO get image from public storage
            record.images = images
