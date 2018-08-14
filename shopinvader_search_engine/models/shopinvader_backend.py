# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = 'shopinvader.backend'

    se_backend_id = fields.Many2one(
        'se.backend',
        'Search Engine Backend')
