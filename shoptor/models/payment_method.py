# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import fields, models


class LocomotivePayment(models.Model):
    _name = 'locomotive.payment'
    _description = 'Locomotive Payment'
    _order = 'sequence'

    payment_method_id = fields.Many2one(
        'payment.method',
        'Payment Method')
    sequence = fields.Integer()
    backend_id = fields.Many2one(
        'locomotive.backend',
        'Backend')


class PaymentMethod(models.Model):
    _inherit = 'payment.method'

    code = fields.Char()
    description = fields.Html()
