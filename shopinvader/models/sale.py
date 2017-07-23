# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
import uuid


class ShopinvaderCartStep(models.Model):
    _name = 'shopinvader.cart.step'
    _description = 'Shopinvader Cart Step'

    name = fields.Char(required=True)
    code = fields.Char(required=True)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    typology = fields.Selection([
        ('sale', 'Sale'),
        ('cart', 'Cart'),
        ], default='sale')
    shopinvader_backend_id = fields.Many2one(
        'locomotive.backend',
        'Backend')
    current_step_id = fields.Many2one(
        'shopinvader.cart.step',
        'Current Cart Step',
        readonly=True)
    done_step_ids = fields.Many2many(
        comodel_name='shopinvader.cart.step',
        string='Done Cart Step',
        readonly=True)
    anonymous_email = fields.Char()
    anonymous_token = fields.Char()
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

    _sql_constraints = [
        ('token_uniq', 'unique(anonymous_token)',
         'Token must be uniq.'),
    ]

    @api.model
    def _prepare_invoice(self, order, lines):
        res = super(SaleOrder, self)._prepare_invoice(order, lines)
        res['shopinvader_backend_id'] = order.shopinvader_backend_id.id
        return res

    @api.multi
    def action_confirm_cart(self):
        for record in self:
            vals = {'typology': 'sale'}
            if record.anonymous_email:
                vals['anonymous_token'] = str(uuid.uuid4())
            record.write(vals)
            if record.shopinvader_backend_id:
                record.shopinvader_backend_id._send_notification(
                    'cart_confirmation', record)
            for transaction in record.transaction_ids:
                # If we confirm the card this mean we come back from the
                # payment provider and so transaction are ready to be captured
                if transaction.state == 'pending':
                    transaction.state = 'to_capture'
        return True

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

    @api.multi
    def action_button_confirm(self):
        res = super(SaleOrder, self).action_button_confirm()
        for record in self:
            if record.state != 'draft' and record.shopinvader_backend_id:
                record.shopinvader_backend_id._send_notification(
                    'sale_confirmation', record)
        return res


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
