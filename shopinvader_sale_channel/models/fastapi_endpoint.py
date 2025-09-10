# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    sale_channel_id = fields.Many2one("sale.channel")
