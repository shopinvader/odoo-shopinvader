# Copyright 2023 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    _sql_constraints = [
        (
            "sale_channel_uniq",
            "unique (sale_channel_id)",
            "Only one backend per sale_channel",
        )
    ]

    sale_channel_id = fields.Many2one(
        "sale.channel",
    )
