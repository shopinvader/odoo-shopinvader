# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class LocomotiveBackend(models.Model):
    _inherit = 'locomotive.backend'

    carrier_ids = fields.Many2many(
        comodel_name='delivery.carrier',
        string='Delivery Carrier')
