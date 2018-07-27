# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ShopInvaderBackend(models.Model):
    _inherit = 'shopinvader.backend'

    use_sale_profile = fields.Boolean(
        default=False,
        help="Determine if this backend use sale profiles",
    )
    sale_profile_ids = fields.One2many(
        'shopinvader.sale.profile',
        'backend_id',
        'Customer sale profiles',
    )
