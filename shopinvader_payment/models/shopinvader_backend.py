# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = 'shopinvader.backend'

    payment_method_ids = fields.One2many(
        'shopinvader.payment',
        'backend_id',
        'Payment Method')

    location = fields.Char(
        required=True
    )
