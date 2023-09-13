# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import sys
from contextlib import contextmanager
from unittest import mock

from fastapi import Depends, FastAPI, status
from fastapi.testclient import TestClient

from odoo import tests

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.fastapi.fastapi_dispatcher import patch_odoo_environment
from odoo.addons.fastapi.tests.common import FastAPITransactionCase
from odoo.addons.fastapi_auth_jwt.dependencies import auth_jwt_default_validator_name
from odoo.addons.shopinvader_fastapi_auth_jwt.dependencies import (
    auth_jwt_authenticated_or_anonymous_partner,
    auth_jwt_authenticated_or_anonymous_partner_autocreate,
)

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

app = FastAPI()


@app.get("/test/shopinvader_auth_jwt_or_anonymous")
def shopinvader_auth_jwt_or_anonymous(
    partner: Annotated[
        Partner,
        Depends(auth_jwt_authenticated_or_anonymous_partner),
    ]
):
    return {"partner_id": partner.id}


@app.get("/test/shopinvader_auth_jwt_or_anonymous_autocreate")
def shopinvader_auth_jwt_or_anonymous_autocreate(
    partner: Annotated[
        Partner,
        Depends(auth_jwt_authenticated_or_anonymous_partner_autocreate),
    ]
):
    return {"partner_id": partner.id}


class TestBase(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "auth_jwt_or_anonymous@shopinvader.com",
            }
        )
        cls.test_anonymous_partner = cls.env[
            "res.partner"
        ]._create_anonymous_partner__cookie(response=mock.MagicMock())
        cls.jwt_validator = cls.env["auth.jwt.validator"].create(
            {
                "name": "test_shopinvader_fastapi_auth_jwt",
                "signature_type": "secret",
                "secret_key": "THESECRET",
                "issuer": "THEISS",
                "audience": "THEAUD",
                "partner_id_strategy": "email",
                # In shopinvader we'll generatlly use partner_id_required=False, so we
                # can have a /signup route with authentication but where the
                # authenticated partner can't be found in the database yet. This means
                # that 'auth_jwt_authenticated_or_anonymous_partner(_autocreate)' will
                # return 401 for valid JWT token but partner unknown.
                "partner_id_required": False,
            }
        )
        app.dependency_overrides[
            auth_jwt_default_validator_name
        ] = lambda: cls.jwt_validator.name
        app.dependency_overrides[odoo_env] = lambda: cls.env
        cls.client = TestClient(app)

    @contextmanager
    def _test_client(self):
        # We need to patch the Odoo environment manager to make
        # use of contextvars instead of thread locals, because
        # the async test client will end up running code in a different thread.
        with patch_odoo_environment():
            yield self.client


@tests.tagged("post_install", "-at_install")
class TestAuthJwtOrAnonymous(TestBase):
    def test_unauthenticated(self) -> None:
        # unauthenticated returns 401
        with self._test_client() as client:
            resp = client.get("/test/shopinvader_auth_jwt_or_anonymous")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)

    def test_jwt_authenticated_valid_partner(self) -> None:
        token = self.jwt_validator._encode(
            {"email": self.test_partner.email},
            secret=self.jwt_validator.secret_key,
            expire=60,
        )
        with self._test_client() as client:
            resp = client.get(
                "/test/shopinvader_auth_jwt_or_anonymous",
                headers={"Authorization": f"Bearer {token}"},
            )
        resp.raise_for_status()
        self.assertEqual(resp.json()["partner_id"], self.test_partner.id, resp.text)

    def test_jwt_authenticated_unknown_partner(self) -> None:
        token = self.jwt_validator._encode(
            {"email": "unknown-" + self.test_partner.email},
            secret=self.jwt_validator.secret_key,
            expire=60,
        )
        with self._test_client() as client:
            resp = client.get(
                "/test/shopinvader_auth_jwt_or_anonymous",
                headers={"Authorization": f"Bearer {token}"},
            )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)

    def test_cookie_valid_anonymous_partner(self) -> None:
        with self._test_client() as client:
            resp = client.get(
                "/test/shopinvader_auth_jwt_or_anonymous",
                headers={
                    "Cookie": "shopinvader-anonymous-partner="
                    + self.test_anonymous_partner.anonymous_token
                },
            )
        resp.raise_for_status()
        self.assertEqual(
            resp.json()["partner_id"], self.test_anonymous_partner.id, resp.text
        )

    def test_cookie_invalid_token(self) -> None:
        with self._test_client() as client:
            resp = client.get(
                "/test/shopinvader_auth_jwt_or_anonymous",
                headers={"Cookie": "shopinvader-anonymous-partner=invalid"},
            )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)

    def test_valid_jwt_valid_cookie(self) -> None:
        """JWT has priority over the anonymous partner cookie."""
        token = self.jwt_validator._encode(
            {"email": self.test_partner.email},
            secret=self.jwt_validator.secret_key,
            expire=60,
        )
        with self._test_client() as client:
            resp = client.get(
                "/test/shopinvader_auth_jwt_or_anonymous",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Cookie": "shopinvader-anonymous-partner="
                    + self.test_anonymous_partner.anonymous_token,
                },
            )
        resp.raise_for_status()
        self.assertEqual(resp.json()["partner_id"], self.test_partner.id, resp.text)

    def test_valid_jwt_invalid_cookie(self) -> None:
        """JWT has priority over the anonymous partner cookie."""
        token = self.jwt_validator._encode(
            {"email": self.test_partner.email},
            secret=self.jwt_validator.secret_key,
            expire=60,
        )
        with self._test_client() as client:
            resp = client.get(
                "/test/shopinvader_auth_jwt_or_anonymous",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Cookie": "shopinvader-anonymous-partner=invalid",
                },
            )
        resp.raise_for_status()
        self.assertEqual(resp.json()["partner_id"], self.test_partner.id, resp.text)

    def test_invalid_jwt_valid_cookie(self) -> None:
        """Invalid JWT has priority over the anonymous partner cookie."""
        token = self.jwt_validator._encode(
            {"email": "unknown-" + self.test_partner.email},
            secret=self.jwt_validator.secret_key,
            expire=60,
        )
        with self._test_client() as client:
            resp = client.get(
                "/test/shopinvader_auth_jwt_or_anonymous",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Cookie": "shopinvader-anonymous-partner=invalid"
                    + self.test_anonymous_partner.anonymous_token,
                },
            )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)

    def test_invalid_jwt_invalid_cookie(self) -> None:
        """JWT has priority over the anonymous partner cookie."""
        token = self.jwt_validator._encode(
            {"email": "unknown-" + self.test_partner.email},
            secret=self.jwt_validator.secret_key,
            expire=60,
        )
        with self._test_client() as client:
            resp = client.get(
                "/test/shopinvader_auth_jwt_or_anonymous",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Cookie": "shopinvader-anonymous-partner=invalid",
                },
            )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)


@tests.tagged("post_install", "-at_install")
class TestAuthJwtOrAnonymousAutocreate(TestBase):
    def test_unauthenticated_creates_anonymous(self) -> None:
        # Unauthenticated creates an anonymous partner and sets the cookie.
        with self._test_client() as client:
            resp = client.get("/test/shopinvader_auth_jwt_or_anonymous_autocreate")
            resp.raise_for_status()
            anonymous_partner_id = resp.json()["partner_id"]
            anonymous_token = resp.cookies["shopinvader-anonymous-partner"]
            self.assertEqual(
                anonymous_token,
                self.env["res.partner"].browse(anonymous_partner_id).anonymous_token,
            )
            # Second call with anonymous partner cookie returns same partner.
            resp = client.get(
                "/test/shopinvader_auth_jwt_or_anonymous_autocreate",
                headers={
                    "Cookie": f"shopinvader-anonymous-partner={anonymous_token}",
                },
            )
            resp.raise_for_status()
            self.assertEqual(resp.json()["partner_id"], anonymous_partner_id)

    def test_jwt_authenticated_valid_partner(self) -> None:
        token = self.jwt_validator._encode(
            {"email": self.test_partner.email},
            secret=self.jwt_validator.secret_key,
            expire=60,
        )
        with self._test_client() as client:
            resp = client.get(
                "/test/shopinvader_auth_jwt_or_anonymous_autocreate",
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
        self.assertEqual(resp.json()["partner_id"], self.test_partner.id, resp.text)

    def test_jwt_authenticated_unknown_partner(self) -> None:
        token = self.jwt_validator._encode(
            {"email": "unknown-" + self.test_partner.email},
            secret=self.jwt_validator.secret_key,
            expire=60,
        )
        with self._test_client() as client:
            resp = client.get(
                "/test/shopinvader_auth_jwt_or_anonymous_autocreate",
                headers={"Authorization": f"Bearer {token}"},
            )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED, resp.text)
