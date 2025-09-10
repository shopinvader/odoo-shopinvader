# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AuthService(models.AbstractModel):
    _inherit = "fastapi.auth.service"

    def _set_auth_cookie(self, auth_partner, request, response):
        rv = super()._set_auth_cookie(auth_partner, request, response)
        # Handle anonymous partner
        cookie_helper = self.env["shopinvader_anonymous_partner.cookie.helper"]
        cookie_helper._promote_anonymous_partner_and_delete_cookie(
            auth_partner.partner_id, request.cookies, response
        )
        return rv
