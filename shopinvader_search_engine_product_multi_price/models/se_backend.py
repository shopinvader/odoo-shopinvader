# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SeBackend(models.Model):

    _inherit = "se.backend"

    pricelist_ids = fields.Many2many("product.pricelist", string="Pricelists")
