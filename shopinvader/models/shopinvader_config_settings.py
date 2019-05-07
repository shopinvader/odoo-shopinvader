# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

PARAMS = [("no_partner_duplicate", "shopinvader.no_partner_duplicate")]


class ShopinvaderConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _name = "shopinvader.config.settings"

    no_partner_duplicate = fields.Boolean(
        default=True,
        help="If checked, when a binding is created for a backend, we first "
        "try to find a partner with the same email and if found we link "
        "the new binding to the first partner found. Otherwise we always "
        "create a new partner",
    )

    @api.multi
    def set_params(self):
        self.ensure_one()
        for field_name, key_name in PARAMS:
            value = getattr(self, field_name, "")
            self.env["ir.config_parameter"].set_param(key_name, value)

    @api.model
    def get_default_params(self, fields):
        res = {}
        for field_name, key_name in PARAMS:
            res[field_name] = (
                self.env["ir.config_parameter"].get_param(key_name, "").strip()
            )
        return res

    # external methods
    @api.model
    def is_partner_duplication_allowed(self):
        param = self.env["ir.config_parameter"].get_param(
            "shopinvader.no_partner_duplicate"
        )
        if not param:
            return self._fields["no_partner_duplicate"].default
        return param == "False"
