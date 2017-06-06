# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shopinvader_backend_id = fields.Many2one(
        'locomotive.backend',
        'Backend')
    cart_state = fields.Char()
    anonymous_email = fields.Char()
    # TODO move this in an extra OCA module
    shipping_amount_total = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)
    shipping_amount_untaxed = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)
    shipping_amount_tax = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)
    item_amount_total = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)
    item_amount_untaxed = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)
    item_amount_tax = fields.Float(
        compute='_compute_shipping',
        dp=dp.get_precision('Account'),
        store=True)

    @api.depends('amount_total', 'amount_untaxed')
    def _compute_shipping(self):
        for record in self:
            record.shipping_amount_untaxed = 0
            record.shipping_amount_total = 0
            record.shipping_amount_tax = 0
            for line in record.order_line:
                if line['is_delivery']:
                    record.shipping_amount_untaxed = line['price_subtotal']
                    # TODO depends on sale order line gross subtotal module
                    # Need to move this code to not depend on this module
                    record.shipping_amount_total = line['price_subtotal_gross']
                    record.shipping_amount_tax = \
                        line['price_subtotal_gross'] - line['price_subtotal']
        for key in ['amount_total', 'amount_untaxed', 'amount_tax']:
            record['item_%s' % key] = record[key] - record['shipping_%s' % key]


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    shopinvader_variant_id = fields.Many2one(
        'shopinvader.variant',
        compute='_compute_shopinvader_variant',
        string='Shopinvader Variant',
        store=True)

    @api.depends('order_id.shopinvader_backend_id', 'product_id')
    def _compute_shopinvader_variant(self):
        for record in self:
            record.shopinvader_variant_id = self.env['shopinvader.variant']\
                .search([
                    ('record_id', '=', record.product_id.id),
                    ('shopinvader_product_id.backend_id', '=',
                        record.order_id.shopinvader_backend_id.id),
                    ])
