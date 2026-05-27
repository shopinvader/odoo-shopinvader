# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models

from ..routers.mass_mailing import mass_mailing_router


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    mailing_list_id = fields.Many2one(
        "mailing.list",
        string="Mass Mailing List",
        help="The mass mailing list to which the contacts created/updated "
        "by this endpoint will be added.",
    )
    is_mass_mailing = fields.Boolean(
        compute="_compute_is_mass_mailing",
    )

    def _compute_is_mass_mailing(self):
        for rec in self:
            rec.is_mass_mailing = mass_mailing_router in rec._get_fastapi_routers()
