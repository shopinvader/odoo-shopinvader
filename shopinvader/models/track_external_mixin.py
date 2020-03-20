# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class TrackExternalMixin(models.AbstractModel):
    _name = "track.external.mixin"
    _description = "Track external update"

    last_external_update_date = fields.Datetime()

    def is_rest_request(self):
        return self.env.context.get("shopinvader_request", False)

    @api.multi
    def _write(self, vals):
        if self.is_rest_request():
            vals["last_external_update_date"] = fields.Datetime.now()
        return super(TrackExternalMixin, self)._write(vals)

    @api.model
    def create(self, vals):
        if self.is_rest_request():
            vals["last_external_update_date"] = fields.Datetime.now()
        return super(TrackExternalMixin, self).create(vals)
