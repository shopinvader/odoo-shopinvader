# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import typing
from datetime import datetime

from odoo import api, models

from odoo.addons.base.models.res_partner import Partner as ResPartner

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


class ShopinvaderAnonymousCookieHelper(models.AbstractModel):
    _name = "shopinvader_anonymous_partner.cookie.helper"
    _description = "Shopinvader Anonymous Partner Cookie Helper"

    @api.model
    def _create_anonymous_partner__cookie(self, response: Response):
        partner = self.env["res.partner"]._create_anonymous_partner__token()
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
        """
        Delete anonymous partner and cookie
        """
        self._get_anonymous_partner__cookie(cookies).unlink()
        response.set_cookie(
            key=COOKIE_NAME,
            max_age=0,
            expires=0,
        )

    @api.model
    def _get_anonymous_partner__cookie(self, cookies: Cookies):
        token = cookies.get(COOKIE_NAME)
        if not token:
            return self.env["res.partner"].sudo().browse()
        return self.env["res.partner"]._get_anonymous_partner__token(token)

    @api.model
    def _promote_anonymous_partner_and_delete_cookie(
        self, partner: ResPartner, cookies: Cookies, response: Response
    ):
        anonymous_partner = self._get_anonymous_partner__cookie(cookies)
        if anonymous_partner:
            partner._promote_from_anonymous_partner(anonymous_partner)
            self._delete_anonymous_partner__cookie(cookies, response)
