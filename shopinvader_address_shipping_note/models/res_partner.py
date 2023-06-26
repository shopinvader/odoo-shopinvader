# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    shipping_note = fields.Char(
        string="Delivery Note",
        help="Instruction for the delivery person in case of absence",
    )
