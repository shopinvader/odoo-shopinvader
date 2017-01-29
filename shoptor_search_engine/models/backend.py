# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class LocomotiveBackend(models.Model):
    _inherit = 'locomotive.backend'

    search_engine = fields.Selection([
        ('algolia', 'Algolia'),
        ])
    search_engine_username = fields.Char()
    search_engine_password = fields.Char()
