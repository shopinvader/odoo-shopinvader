# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import secrets
import typing

from odoo import _, api, fields, models

COOKIE_NAME = "shopinvader-anonymous-partner"
COOKIE_MAX_AGE = 86400 * 365


class Response(typing.Protocol):
    def set_cookie(
        self,
        key: str,
        value: str,
        max_age: int,
        secure: bool,
        httponly: bool,
        samesite: typing.Literal["lax", "strict", "none"],
    ) -> None:
        ...


class Cookies(typing.Protocol):
    def get(self, key: str) -> typing.Optional[str]:
        ...


class ResPartner(models.Model):

    _inherit = "res.partner"

    anonymous_token = fields.Char()

    _sql_constraints = [
        (
            "anonymous_token_unique",
            "EXCLUDE (anonymous_token WITH =) WHERE (anonymous_token IS NOT NULL)",
            "This token is already used!",
        )
    ]

    @api.model
    def _create_anonymous_partner(self, response: Response):
        token = secrets.token_hex(32)
        partner = (
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
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            max_age=COOKIE_MAX_AGE,
            samesite="strict",
            secure=True,
            httponly=True,
        )
        return partner

    @api.model
    def _get_anonymous_partner(self, cookies: Cookies):
        token = cookies.get(COOKIE_NAME)
        if not token:
            return self.env["res.partner"].sudo().browse()
        return (
            self.env["res.partner"]
            .sudo()
            .with_context(active_test=False)
            .search([("anonymous_token", "=", token)], limit=1)
        )
