# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp
import uuid
import logging
from openerp.tools.translate import _
_logger = logging.getLogger(__name__)


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
    anonymous_token = fields.Char(copy=False)
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
    shopinvader_state = fields.Selection([
        ('cancel', 'Cancel'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ], compute='_compute_shopinvader_state',
        store=True)

    _sql_constraints = [
        ('token_uniq', 'unique(anonymous_token)',
         'Token must be uniq.'),
    ]

    def is_anonymous(self):
        self.ensure_one()
        return self.partner_id ==\
            self.shopinvader_backend_id.anonymous_partner_id

    def _get_shopinvader_state(self):
        self.ensure_one()
        if self.state == 'cancel':
            return 'cancel'
        elif self.shipped:
            return 'shipped'
        elif self.state == 'draft':
            return 'pending'
        else:
            return 'processing'

    @api.depends('state', 'shipped')
    def _compute_shopinvader_state(self):
        # simple way to have more human friendly name for
        # the sale order on the website
        for record in self:
            record.shopinvader_state = record._get_shopinvader_state()

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

    def reset_cart_lines(self):
        for record in self:
            record.order_line.reset_price_tax()

    def _play_cart_onchange(self, vals):
        result = {}
        # TODO in 10 use and improve onchange helper module
        if 'partner_id' in vals:
            res = self.onchange_partner_id(vals['partner_id']).get('value', {})
            for key in ['pricelist_id', 'payment_term']:
                if key in res:
                    result[key] = res[key]
        if 'partner_shipping_id' in vals:
            res = self.onchange_delivery_id(
                self.company_id.id,
                vals.get('partner_id') or self.partner_id.id,
                vals['partner_shipping_id'], None).get('value', {})
            if 'fiscal_position' in res:
                result['fiscal_position'] = res['fiscal_position']
        return result

    def _need_to_reset_tax_price_on_line(self, vals):
        reset = False
        for field in ['fiscal_position', 'pricelist_id']:
            if field in vals and self[field].id != vals[field]:
                reset = True
        return reset

    def _prepare_available_carrier(self, carrier):
        return {
            'id': carrier.id,
            'name': carrier.name,
            'description': carrier.description,
            'price': carrier.price,
            }

    def _get_available_carrier(self):
        self.ensure_one()
        if self.is_anonymous():
            return []
        else:
            carriers = self.with_context(order_id=self.id)\
                .env['delivery.carrier'].search([])
            res = [self._prepare_available_carrier(carrier)
                   for carrier in carriers
                   if carrier.available]
            return sorted(res, key=lambda x: (x['price'], x['name']))

    def _update_default_carrier(self):
        if self.is_anonymous():
            return
        carrier_ids = [x['id'] for x in self._get_available_carrier()]
        if not self.carrier_id and carrier_ids:
            self.carrier_id = carrier_ids[0]
        elif self.carrier_id.id not in carrier_ids:
            _logger.debug('Update obsolet carrier for sale order %s', self.id)
            if carrier_ids:
                self.carrier_id = carrier_ids[0]
            else:
                self.carrier_id = False
                self.env['sale.order.line'].search([
                    ('order_id', '=', self.id),
                    ('is_delivery', '=', True)]).unlink()
        if self.carrier_id:
            self.delivery_set()

    def _check_allowed_carrier(self, vals):
        carrier_ids = [x['id'] for x in self._get_available_carrier()]
        if 'carrier_id' in vals:
            if vals['carrier_id'] not in carrier_ids:
                raise UserError(
                    _('Invalid carrier delivey method for your country'))

    @api.multi
    def write_with_onchange(self, vals):
        self.ensure_one()
        vals.update(self._play_cart_onchange(vals))
        reset = self._need_to_reset_tax_price_on_line(vals)
        self.write(vals)
        if 'payment_method_id' in vals:
            self.onchange_payment_method_set_workflow()
        self._update_default_carrier()
        if 'carrier_id' in vals:
            self._check_allowed_carrier(vals)
            self.delivery_set()
        if reset:
            self.reset_cart_lines()
        return True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    shopinvader_variant_id = fields.Many2one(
        'shopinvader.variant',
        compute='_compute_shopinvader_variant',
        string='Shopinvader Variant',
        store=True)

    def reset_price_tax(self):
        reset_carrier = False
        for line in self:
            if line.is_delivery:
                reset_carrier = True
                continue
            res = line.product_id_change(
                line.order_id.pricelist_id.id,
                line.product_id.id,
                qty=line.product_uom_qty,
                uom=line.product_uom.id,
                qty_uos=line.product_uos_qty,
                uos=line.product_uos.id,
                name=line.name,
                partner_id=line.order_id.partner_id.id,
                lang=False,
                update_tax=True,
                date_order=line.order_id.date_order,
                packaging=False,
                fiscal_position=line.order_id.fiscal_position.id,
                flag=True)['value']
            line.write({
                'price_unit': res['price_unit'],
                'discount': res.get('discount'),
                'tax_id': [(6, 0, res.get('tax_id', []))]
                })
        if reset_carrier:
            self.mapped('order_id').delivery_set()

    @api.depends('order_id.shopinvader_backend_id', 'product_id')
    def _compute_shopinvader_variant(self):
        for record in self:
            record.shopinvader_variant_id = self.env['shopinvader.variant']\
                .search([
                    ('record_id', '=', record.product_id.id),
                    ('shopinvader_product_id.backend_id', '=',
                        record.order_id.shopinvader_backend_id.id),
                    ])
