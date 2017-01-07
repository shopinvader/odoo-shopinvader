# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp import SUPERUSER_ID


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    locomotivecms_bind_ids = fields.One2many(
        'locomotivecms.product',
        'record_id',
        string='Locomotive Binding')


class LocomotivecmsProduct(models.Model):
    _name = 'locomotivecms.product'
    _inherit = 'locomotivecms.binding'
    _inherits = {'product.template': 'record_id'}

    record_id = fields.Many2one(
        'product.template',
        required=True,
        ondelete='cascade')

    _sql_constraints = [
        ('record_uniq', 'unique(backend_id, record_id)',
         'A product can only have one binding by backend.'),
    ]

    # Automatically create the locomotive binding for the image
    @api.model
    def create(self, vals):
        binding = super(LocomotivecmsProduct, self).create(vals)
        binding_image_obj = \
            self.env['locomotivecms.image'].with_context(
                connector_no_export=True)
        for image in binding.image_ids:
            for size in binding_image_obj._image_size:
                binding_image_obj.create({
                    'size': size,
                    'record_id': image.id,
                    'backend_id': binding.backend_id.id,
                    })
        return binding


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
        self.ensure_one()
        res = []
        items = self.env['product.pricelist.item'].search([
            ('price_version_id.pricelist_id', '=', pricelist.id)
            ])
        item_qty = set([item.min_quantity
                        for item in items if item.min_quantity > 1] + [1])
        for qty in item_qty:
            res.append({
                'qty': qty,
                'price': self._get_rounded_price(pricelist, qty, tax_included),
                })
        return res
