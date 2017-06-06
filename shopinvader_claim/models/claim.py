# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class CrmClaim(models.Model):
    _inherit = "crm.claim"

    shopinvader_backend_id = fields.Many2one(
        'locomotive.backend',
        'Backend')
