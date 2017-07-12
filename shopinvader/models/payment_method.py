# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import fields, models


class ShopinvaderPayment(models.Model):
    _name = 'shopinvader.payment'
    _description = 'Shopinvader Payment'
    _order = 'sequence'

    payment_method_id = fields.Many2one(
        'payment.method',
        'Payment Method')
    sequence = fields.Integer()
    backend_id = fields.Many2one(
        'locomotive.backend',
        'Backend')
    notification = fields.Selection([
        ('cart_confirmation', 'Cart Validation'),
        ('sale_confirmation', 'Sale Confirmation'),
        ('cart_confirmation_and_sale_confirmation',
         'Cart and Sale Confirmation'),
        ])
    manual = fields.Boolean()


class PaymentMethod(models.Model):
    _inherit = 'payment.method'

    code = fields.Char()
    description = fields.Html()
    show_description_after_validation = fields.Boolean()
