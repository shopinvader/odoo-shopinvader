# Copyright 2020 ForgeFlow S.L. (http://www.forgeflow.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    allowed_country_state_ids = fields.Many2many(
        comodel_name="res.country.state",
        string="Allowed Country States",
        domain="[('country_id','in',allowed_country_ids)]",
    )
