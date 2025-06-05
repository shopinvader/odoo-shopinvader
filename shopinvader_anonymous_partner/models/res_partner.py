# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import secrets

from odoo import _, api, fields, models

from odoo.addons.base.models.res_partner import Partner as ResPartner


class ResPartner(models.Model):
    _inherit = "res.partner"

    anonymous_token = fields.Char(
        help="Token used to uniquely and securely identify anonymous partners."
    )

    _sql_constraints = [
        (
            "anonymous_token_unique",
            "UNIQUE(anonymous_token)",
            "This token is already used!",
        )
    ]

    @api.model
    def _create_anonymous_partner__token(self):
        token = secrets.token_hex(32)
        return (
            self.env["res.partner"]
            .sudo()
            .create(
                {
                    "name": _("Anonymous (%s)") % (token[:8],),
                    "anonymous_token": token,
                    "active": False,
                }
            )
        )

    @api.model
    def _get_anonymous_partner__token(self, token: str):
        return (
            self.env["res.partner"]
            .sudo()
            .with_context(active_test=False)
            .search([("anonymous_token", "=", token)], limit=1)
        )

    def _promote_from_anonymous_partner(self, anonymous_partner: ResPartner):
        """
        Promote an anonymous partner to an authenticated partner.

        This method should be overridden by other modules to implement
        the partner resolution logic, merging the anonymous partner cart
        for instance.
        """
