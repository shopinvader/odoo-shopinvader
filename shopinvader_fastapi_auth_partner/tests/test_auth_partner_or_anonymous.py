# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import sys
from unittest import mock

from fastapi import Depends, FastAPI, status

from odoo import tests

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi_auth_partner.tests.test_auth import CommonTestAuth
from odoo.addons.shopinvader_fastapi_auth_partner.dependencies import (
    auth_partner_authenticated_or_anonymous_partner,
    auth_partner_authenticated_or_anonymous_partner_autocreate,
)

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

app = FastAPI()


@app.get("/test/shopinvader_auth_partner_or_anonymous")
def shopinvader_auth_partner_or_anonymous(
    partner: Annotated[
        Partner,
        Depends(auth_partner_authenticated_or_anonymous_partner),
    ]
):
    return {"partner_id": partner.id}


@app.get("/test/shopinvader_auth_partner_or_anonymous_autocreate")
def shopinvader_auth_partner_or_anonymous_autocreate(
    partner: Annotated[
        Partner,
        Depends(auth_partner_authenticated_or_anonymous_partner_autocreate),
    ]
):
    return {"partner_id": partner.id}


class TestBase(CommonTestAuth):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_anonymous_partner = cls.env[
            "res.partner"
        ]._create_anonymous_partner__cookie(response=mock.MagicMock())
        cls.default_fastapi_app = app
        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "Loriot",
                "email": "loriot@example.org",
                "auth_partner_ids": [
                    (
                        0,
                        0,
                        {
                            "password": "supersecret",
                            "directory_id": cls.demo_app.directory_id.id,
                        },
                    )
                ],
            }
        )

    def _add_anonymous_cookie(self, client, force_value=None):
        client.cookies.set(
            "shopinvader-anonymous-partner",
            force_value or self.test_anonymous_partner.anonymous_token,
        )


@tests.tagged("post_install", "-at_install")
class TestAuthPartnerOrAnonymous(TestBase):
    def test_unauthenticated(self) -> None:
        # unauthenticated returns 401
        with self._create_test_client() as client:
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)

    def test_partner_authenticated_valid_partner(self) -> None:
        with self._create_test_client() as client:
            self._login(client)
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous")
        resp.raise_for_status()
        self.assertEqual(resp.json()["partner_id"], self.test_partner.id, resp.text)

    def test_partner_authenticated_unknown_partner(self) -> None:
        with self._create_test_client() as client:
            self._login(client)
            # The account of the partner have been deleted and the partner try
            # to reconnect with an old cookie
            self.test_partner.unlink()
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)

    def test_cookie_valid_anonymous_partner(self) -> None:
        with self._create_test_client() as client:
            self._add_anonymous_cookie(client)
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous")
        resp.raise_for_status()
        self.assertEqual(
            resp.json()["partner_id"], self.test_anonymous_partner.id, resp.text
        )

    def test_cookie_invalid_token(self) -> None:
        with self._create_test_client() as client:
            self._add_anonymous_cookie(client, "invalid_cookie")
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)

    def test_valid_partner_valid_cookie(self) -> None:
        """Auth partner has priority over the anonymous partner cookie."""
        with self._create_test_client() as client:
            self._login(client)
            self._add_anonymous_cookie(client)
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous")
        resp.raise_for_status()
        self.assertEqual(resp.json()["partner_id"], self.test_partner.id, resp.text)

    def test_valid_partner_invalid_cookie(self) -> None:
        """Auth Partner has priority over the anonymous partner cookie."""
        with self._create_test_client() as client:
            self._login(client)
            self._add_anonymous_cookie(client, "invalid_cookie")
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous")
        resp.raise_for_status()
        self.assertEqual(resp.json()["partner_id"], self.test_partner.id, resp.text)

    def test_invalid_partner_valid_cookie(self) -> None:
        """Invalid Auth Partner has priority over the anonymous partner cookie."""
        with self._create_test_client() as client:
            self._login(client)
            self.test_partner.unlink()
            self._add_anonymous_cookie(client)
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)

    def test_invalid_partner_invalid_cookie(self) -> None:
        """Auth Partner has priority over the anonymous partner cookie."""
        with self._create_test_client() as client:
            self._login(client)
            self.test_partner.unlink()
            self._add_anonymous_cookie(client, "invalid_cookie")
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)


@tests.tagged("post_install", "-at_install")
class TestAuthJwtOrAnonymousAutocreate(TestBase):
    def test_unauthenticated_creates_anonymous(self) -> None:
        # Unauthenticated creates an anonymous partner and sets the cookie.
        with self._create_test_client() as client:
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous_autocreate")
            resp.raise_for_status()
            anonymous_partner_id = resp.json()["partner_id"]
            anonymous_token = resp.cookies["shopinvader-anonymous-partner"]
            self.assertEqual(
                anonymous_token,
                self.env["res.partner"].browse(anonymous_partner_id).anonymous_token,
            )
            # Second call with anonymous partner cookie returns same partner.
            resp = client.get(
                "/test/shopinvader_auth_partner_or_anonymous_autocreate",
                headers={
                    "Cookie": f"shopinvader-anonymous-partner={anonymous_token}",
                },
            )
            resp.raise_for_status()
            self.assertEqual(resp.json()["partner_id"], anonymous_partner_id)

    def test_partner_authenticated_valid_partner(self) -> None:
        with self._create_test_client() as client:
            self._login(client)
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous_autocreate")
            resp.raise_for_status()
        self.assertEqual(resp.json()["partner_id"], self.test_partner.id, resp.text)

    def test_partner_authenticated_unknown_partner(self) -> None:
        with self._create_test_client() as client:
            self._login(client)
            self.test_partner.unlink()
            resp = client.get("/test/shopinvader_auth_partner_or_anonymous_autocreate")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)
