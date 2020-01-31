# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    privacy_activity_id = fields.Many2one(
        comodel_name="privacy.activity",
        string="Privacy Activity",
        help="This is the Privacy Activity related to this backend.",
    )
    privacy_consent_ids = fields.One2many(
        comodel_name="privacy.consent",
        related="privacy_activity_id.consent_ids",
        readonly=True,
    )

    @api.model
    def _get_default_privacy_activity_values(self, values):
        return {"name": values.get("name") or "/"}

    @api.model
    def create(self, vals):
        """
        If the privacy activity is not passed in parameters, create it.
        :return:
        """
        if not vals.get("privacy_activity_id"):
            activity_id = self.env["privacy.activity"].create(
                self._get_default_privacy_activity_values(vals)
            )
            vals.update({"privacy_activity_id": activity_id.id})
        return super(ShopinvaderBackend, self).create(vals)
