# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    token_validity = fields.Integer(
        string="Token validity (minutes)",
        default=20,
    )

    @api.constrains("token_validity")
    def _constrains_token_validity(self):
        """
        Constrain function for the field token_validity
        :return:
        """
        bad_records = self.filtered(lambda r: r.token_validity < 1)
        if bad_records:
            details = "\n- ".join(bad_records.mapped("display_name"))
            message = _("Minimum token validity is 1 minute:\n- %s") % details
            raise exceptions.ValidationError(message)
