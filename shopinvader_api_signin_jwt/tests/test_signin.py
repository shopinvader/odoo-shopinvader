# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from contextlib import contextmanager

import jwt

from odoo.addons.fastapi.tests.common import FastAPITransactionCase
from odoo.addons.fastapi_auth_jwt.dependencies import auth_jwt_default_validator_name

from ..routers import signin_router


class SigninCase(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.default_fastapi_odoo_env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                queue_job__no_delay=True,
            )
        )

        api_signin_jwt_group = cls.env.ref(
            "shopinvader_api_signin_jwt.shopinvader_signin_user_group"
        )
        user_with_rights = cls.env["res.users"].create(
            {
                "name": "Test User With Rights",
                "login": "user_with_rights",
                "groups_id": [(6, 0, [api_signin_jwt_group.id])],
            }
        )

        cls.default_fastapi_running_user = user_with_rights
        cls.default_fastapi_router = signin_router
        cls.default_fastapi_dependency_overrides = {
            auth_jwt_default_validator_name: (lambda: "test")
        }

    def _get_token(self, validator):
        payload = {
            "aud": validator.audience,
            "iss": validator.issuer,
            "exp": time.time() + 60,
            "email": "test@mail.com",
            "name": "Test partner",
            "email_verified": True,
        }
        access_token = jwt.encode(
            payload,
            key=validator.secret_key,
            algorithm=validator.secret_algorithm,
        )
        return "Bearer " + access_token

    @contextmanager
    def _validator(self):
        validator = self.env["auth.jwt.validator"].create(
            {
                "name": "test",
                "audience": "auth_jwt_test_signin_api",
                "issuer": "testissuer",
                "signature_type": "secret",
                "secret_algorithm": "HS256",
                "secret_key": "thesecret012345678901234567890123456789",
                "user_id_strategy": "static",
                "static_user_id": self.env.ref("base.user_demo").id,
                "partner_id_strategy": "email",
                "partner_id_required": False,
            }
        )
        try:
            yield validator
        finally:
            validator.unlink()

    def test_signin(self):
        with self._validator() as validator:
            token = self._get_token(validator)
            partner = self.env["res.partner"].search([("email", "=", "test@mail.com")])
            self.assertFalse(partner)
            # Call signin with unknown partner
            with self._create_test_client() as client:
                res = client.post("/signin", headers={"Authorization": token})
            self.assertEqual(res.status_code, 201)
            partner = self.env["res.partner"].search([("email", "=", "test@mail.com")])
            self.assertTrue(partner)
            self.assertEqual(partner.name, "Test partner")
            # Try again now that partner exists
            with self._create_test_client() as client:
                res = client.post("/signin", headers={"Authorization": token})
            self.assertEqual(res.status_code, 200)

    def test_signout(self):
        with self._validator() as validator:
            validator.write({"cookie_enabled": True, "cookie_name": "test_cookie"})
            token = self._get_token(validator)
            with self._create_test_client() as client:
                res = client.post("/signin", headers={"Authorization": token})
            cookie = res.cookies.get("test_cookie")
            self.assertTrue(cookie)
            with self._create_test_client() as client:
                res = client.post("/signout")
            cookie = res.cookies.get("test_cookie")
            self.assertFalse(cookie)
