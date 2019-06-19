# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    tax_mapping_ids = fields.One2many(
        string="Taxes",
        comodel_name="shopinvader.tax.mapping",
        inverse_name="backend_id",
    )
