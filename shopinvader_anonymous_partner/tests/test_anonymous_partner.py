# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from unittest import mock

import psycopg2

from odoo.http import Controller, request, route
from odoo.tests.common import HttpCase, TransactionCase
from odoo.tools import mute_logger

from odoo.addons.shopinvader_anonymous_partner.models.cookie_helper import COOKIE_NAME


class TestController(Controller):
    @route("/test/anonymous_partner_create", type="http", auth="none")
    def anonymous_partner_create(self):
        cookie_helper = request.env["shopinvader_anonymous_partner.cookie.helper"]
        partner = cookie_helper._create_anonymous_partner__cookie(
            request.future_response
        )
        return str(partner.id)

    @route("/test/anonymous_partner_get", type="http", auth="none")
    def anonymous_partner_get(self):
        cookie_helper = request.env["shopinvader_anonymous_partner.cookie.helper"]
        partner = cookie_helper._get_anonymous_partner__cookie(
            request.httprequest.cookies
        )
        if partner:
            return str(partner.id)
        return ""

    @route("/test/anonymous_partner_delete", type="http", auth="none")
    def anonymous_partner_delete(self):
        cookie_helper = request.env["shopinvader_anonymous_partner.cookie.helper"]
        cookie_helper._delete_anonymous_partner__cookie(
            request.httprequest.cookies, request.future_response
        )


class TestShopinvaderAnonymousPartner(TransactionCase):
    def test_create(self):
        cookie_helper = self.env["shopinvader_anonymous_partner.cookie.helper"]
        partner = cookie_helper._create_anonymous_partner__cookie(mock.MagicMock())
        self.assertEqual(len(partner), 1)
        self.assertTrue(partner.anonymous_token)

    @mute_logger("odoo.sql_db")
    def test_create_duplicate_token(self):
        cookie_helper = self.env["shopinvader_anonymous_partner.cookie.helper"]
        partner = cookie_helper._create_anonymous_partner__cookie(mock.MagicMock())
        with self.assertRaises(psycopg2.errors.UniqueViolation):
            self.env["res.partner"].create(
                {
                    "name": "test",
                    "anonymous_token": partner.anonymous_token,
                }
            )

    def test_get(self):
        cookie_helper = self.env["shopinvader_anonymous_partner.cookie.helper"]
        partner = cookie_helper._create_anonymous_partner__cookie(mock.MagicMock())
        partner2 = cookie_helper._get_anonymous_partner__cookie(
            cookies={COOKIE_NAME: partner.anonymous_token}
        )
        self.assertEqual(partner, partner2)
        partner2 = cookie_helper._get_anonymous_partner__cookie(
            cookies={COOKIE_NAME: None}
        )
        self.assertEqual(len(partner2), 0)

    def test_delete(self):
        cookie_helper = self.env["shopinvader_anonymous_partner.cookie.helper"]
        partner = cookie_helper._create_anonymous_partner__cookie(mock.MagicMock())
        self.assertTrue(partner.exists())
        cookie_helper._delete_anonymous_partner__cookie(
            cookies={COOKIE_NAME: partner.anonymous_token}, response=mock.MagicMock()
        )
        self.assertFalse(partner.exists())

    def test_promote(self):
        cookie_helper = self.env["shopinvader_anonymous_partner.cookie.helper"]
        anonymous_partner = cookie_helper._create_anonymous_partner__cookie(
            mock.MagicMock()
        )
        self.assertTrue(anonymous_partner.exists())

        partner = self.env["res.partner"].create(
            {"name": "Test promotion partner", "email": "test+promotion@example.com"}
        )
        with mock.patch.object(
            type(self.env["res.partner"]), "_promote_from_anonymous_partner"
        ) as mock_promote:
            cookie_helper = self.env["shopinvader_anonymous_partner.cookie.helper"]
            cookie_helper._promote_anonymous_partner_and_delete_cookie(
                partner,
                cookies={COOKIE_NAME: anonymous_partner.anonymous_token},
                response=mock.MagicMock(),
            )
            mock_promote.assert_called_with(anonymous_partner)

        self.assertFalse(anonymous_partner.exists())


class TestShopinvaderAnonymousPartnerEndToEnd(HttpCase):
    def test_create_and_get_and_delete(self):
        resp = self.url_open("/test/anonymous_partner_create")
        resp.raise_for_status()
        token = resp.cookies.get(COOKIE_NAME)
        self.assertTrue(token)
        partner_id = int(resp.text)
        self.assertTrue(partner_id)
        # get without cookie
        resp = self.url_open("/test/anonymous_partner_get")
        resp.raise_for_status()
        self.assertEqual(resp.text, "", resp.text)
        # get with cookie
        resp = self.url_open(
            "/test/anonymous_partner_get",
            headers={"Cookie": f"{COOKIE_NAME}={token}"},
        )
        resp.raise_for_status()
        self.assertEqual(int(resp.text), partner_id)
        # delete cookie
        resp = self.url_open("/test/anonymous_partner_delete")
        resp.raise_for_status()
        self.assertFalse(resp.cookies.get(COOKIE_NAME))
