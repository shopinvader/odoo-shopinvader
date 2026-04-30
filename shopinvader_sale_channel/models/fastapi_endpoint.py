# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    sale_channel_id = fields.Many2one(
        "sale.channel",
        help="Sale channel associated with this FastAPI endpoint.",
    )

    def _get_app_context(self):
        return {
            **super()._get_app_context(),
            "sale_channel_id": self.sale_channel_id.id,
        }
