# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopinvaderPartner(models.Model):
    _inherit = "shopinvader.partner"

    first_active_date = fields.Datetime(
        string="First Activity on",
        help="Date of the first user activity",
        readonly=True,
    )
    last_active_date = fields.Datetime(
        string="Last Activity on",
        help="Date of the last user activity",
        readonly=True,
    )

    def _log_active_date(self):
        self.ensure_one()
        self.last_active_date = fields.Datetime.now()
        if not self.first_active_date:
            self.first_active_date = self.last_active_date
