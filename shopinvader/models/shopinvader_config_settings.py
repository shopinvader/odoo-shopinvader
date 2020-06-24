# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"
    _name = "shopinvader.config.settings"
    _description = "Shopinvader configuration"

    no_partner_duplicate = fields.Boolean(
        default=True,
        config_parameter="shopinvader.no_partner_duplicate",
        help="If checked, when a binding is created for a backend, we first "
        "try to find a partner with the same email and if found we link "
        "the new binding to the first partner found. Otherwise we always "
        "create a new partner",
    )

    # external methods
    @api.model
    def is_partner_duplication_allowed(self):
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("shopinvader.no_partner_duplicate")
        )
        if not param:
            return self._fields["no_partner_duplicate"].default
        return param == "False"
