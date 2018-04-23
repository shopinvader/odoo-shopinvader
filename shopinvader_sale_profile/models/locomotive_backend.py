# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class LocomotiveBackend(models.Model):
    _inherit = 'locomotive.backend'

    use_sale_profile = fields.Boolean(
        default=False,
        help="Determine if this backend use sale profiles",
    )
    sale_profile_ids = fields.One2many(
        'shopinvader.sale.profile',
        'backend_id',
        'Customer sale profiles',
    )
