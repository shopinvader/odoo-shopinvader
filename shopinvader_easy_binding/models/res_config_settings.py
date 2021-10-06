# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    shopinvader_company_backend_id = fields.Many2one(
        related="company_id.shopinvader_company_backend_id",
        readonly=False,
        domain="[('company_id', '=', company_id)]",
    )
