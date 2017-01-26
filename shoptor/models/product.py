# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp import SUPERUSER_ID


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    locomotive_bind_ids = fields.One2many(
        'locomotive.product',
        'record_id',
        string='Locomotive Binding')


class LocomotiveProduct(models.Model):
    _name = 'locomotive.product'
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
    meta_keyword = fields.Char()

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id)',
         'A product can only have one binding by backend.'),
    ]

    # Automatically create the locomotive binding for the image
    @api.model
    def create(self, vals):
        binding = super(LocomotiveProduct, self).create(vals)
        binding_image_obj = \
            self.env['locomotive.image'].with_context(
                connector_no_export=True)
        for image in binding.image_ids:
            for size in binding_image_obj._image_size:
                binding_image_obj.create({
                    'size': size,
                    'record_id': image.id,
                    'backend_id': binding.backend_id.id,
                    })
        return binding

    @api.depends('url_builder', 'record_id.name')
    def _compute_url(self):
        return super(LocomotiveProduct, self)._compute_url()


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
            'locomotive.product',
            ))],
        translate=True)
    help = fields.Html(translate=True)
    name = fields.Char(related='field_id.field_description')
