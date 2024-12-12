# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time

import jwt

from odoo.addons.fastapi.tests.common import FastAPITransactionCase
from odoo.addons.fastapi_auth_jwt.dependencies import auth_jwt_default_validator_name
from odoo.addons.shopinvader_anonymous_partner.models.res_partner import COOKIE_NAME

from ..routers import signin_router


class SigninCase(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

        cls.validator = cls.env["auth.jwt.validator"].create(
            {
                "name": "test",
                "audience": "auth_jwt_test_signin_api",
                "issuer": "testissuer",
                "signature_type": "secret",
                "secret_algorithm": "HS256",
                "secret_key": "secret",
                "user_id_strategy": "static",
                "static_user_id": cls.env.ref("base.user_demo").id,
                "partner_id_strategy": "email",
                "partner_id_required": False,
            }
        )

        cls.default_fastapi_running_user = user_with_rights
        cls.default_fastapi_router = signin_router
        cls.default_fastapi_dependency_overrides = {
            auth_jwt_default_validator_name: (lambda: "test")
        }

    def _get_token(self):
        payload = {
            "aud": self.validator.audience,
            "iss": self.validator.issuer,
            "exp": time.time() + 60,
            "email": "test@mail.com",
            "name": "Test partner",
            "email_verified": True,
        }
        access_token = jwt.encode(
            payload,
            key=self.validator.secret_key,
            algorithm=self.validator.secret_algorithm,
        )
        return "Bearer " + access_token

    def test_signin(self):
        token = self._get_token()
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

    def test_signin_anonymous_cart(self):
        anonymous_partner = self.env["res.partner"].create(
            {"name": "Test anonymous", "anonymous_token": "1234", "active": False}
        )
        product = self.env["product.product"].create(
            {"name": "product", "uom_id": self.env.ref("uom.product_uom_unit").id}
        )
        anonymous_cart = self.env["sale.order"].create(
            {
                "partner_id": anonymous_partner.id,
                "order_line": [
                    (0, 0, {"product_id": product.id, "product_uom_qty": 1}),
                ],
                "typology": "cart",
            }
        )

        token = self._get_token()
        with self._create_test_client() as client:
            res = client.post(
                "/signin",
                headers={"Authorization": token},
                cookies={COOKIE_NAME: "1234"},
            )
        self.assertFalse(res.cookies.get(COOKIE_NAME))
        self.assertFalse(anonymous_partner.exists())
        self.assertFalse(anonymous_cart.exists())
        partner = self.env["res.partner"].search([("email", "=", "test@mail.com")])
        cart = self.env["sale.order"].search([("partner_id", "=", partner.id)])
        self.assertEqual(len(cart.order_line), 1)
        self.assertEqual(cart.order_line[0].product_id, product)

    def test_signout(self):
        self.validator.write({"cookie_enabled": True, "cookie_name": "test_cookie"})
        token = self._get_token()
        with self._create_test_client() as client:
            res = client.post("/signin", headers={"Authorization": token})
        cookie = res.cookies.get("test_cookie")
        self.assertTrue(cookie)
        with self._create_test_client() as client:
            res = client.post("/signout")
        cookie = res.cookies.get("test_cookie")
        self.assertFalse(cookie)
