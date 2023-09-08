# Copyright 2023 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleChannel(models.Model):
    _inherit = "sale.channel"

    shopinvader_backend_ids = fields.One2many(
        # is a one2one relation
        comodel_name="shopinvader.backend",
        inverse_name="sale_channel_id",
    )
