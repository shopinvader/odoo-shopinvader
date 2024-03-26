# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import secrets
import typing
from datetime import datetime

from odoo import _, api, fields, models

COOKIE_NAME = "shopinvader-anonymous-partner"
COOKIE_MAX_AGE = 86400 * 365


class Response(typing.Protocol):
    def set_cookie(
        self,
        key: str,
        value: str,
        max_age: int,
        expires: datetime | str | int,
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
    def _create_anonymous_partner__cookie(self, response: Response):
        partner = self._create_anonymous_partner__token()
        response.set_cookie(
            key=COOKIE_NAME,
            value=partner.anonymous_token,
            max_age=COOKIE_MAX_AGE,
            samesite="strict",
            secure=True,
            httponly=True,
        )
        return partner

    @api.model
    def _delete_anonymous_partner__cookie(self, cookies: Cookies, response: Response):
        self._get_anonymous_partner__cookie(cookies).unlink()
        response.set_cookie(
            key=COOKIE_NAME,
            max_age=0,
            expires=0,
        )

    @api.model
    def _get_anonymous_partner__token(self, token: str):
        return (
            self.env["res.partner"]
            .sudo()
            .with_context(active_test=False)
            .search([("anonymous_token", "=", token)], limit=1)
        )

    @api.model
    def _get_anonymous_partner__cookie(self, cookies: Cookies):
        token = cookies.get(COOKIE_NAME)
        if not token:
            return self.env["res.partner"].sudo().browse()
        return self._get_anonymous_partner__token(token)
