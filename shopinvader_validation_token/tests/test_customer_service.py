# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4

from odoo import exceptions

from ..tests.common import CommonValidationToken


class TestCustomerService(CommonValidationToken):
    def _get_usage(self):
        return "customer"

    def _get_partner(self):
        return self.env.ref("shopinvader.partner_1")

    @classmethod
    def _get_notification_type(cls):
        return "partner_token_customer"

    @classmethod
    def setUpClass(cls):
        super(TestCustomerService, cls).setUpClass()
        cls.data.update(
            {
                "external_id": "D5CdkqOEL",
                "email": "new-token@customer.example.com",
            }
        )

    def test_create_no_token(self):
        """
        Ensure customer still working when token security notification is
        disabled
        :return:
        """
        self._disable_security_token()
        res = self.service.dispatch("create", params=self.data.copy())["data"]
        partner = self.env["res.partner"].browse(res["id"])
        self.assertEqual(partner.email, self.data.copy()["email"])
        first_binding = partner.shopinvader_bind_ids
        self.assertTrue(first_binding.exists())

    def test_create_with_token1(self):
        """
        For this case, try to create a customer without token when this token
        is mandatory but not filled (cfr config).
        :return:
        """
        self._enable_security_token()
        with self.assertRaises(exceptions.UserError) as em:
            result = self.service.dispatch(
                "security_code_enabled", params=self.data.copy()
            )
            self.assertTrue(result.get("ask_security_code"))
            self.service.dispatch("create", params=self.data.copy())
        self.assertIn("Invalid/Expired token", em.exception.name)

    def test_create_with_token2(self):
        """
        For this case, try to create a customer with token required
        :return:
        """
        self._enable_security_token()
        token = str(uuid4())
        with self._patch_get_new_token(forced_token=token):
            self.service.dispatch(
                "security_code_enabled", params=self.data.copy()
            )
            data = self.data.copy()
            data.update({"token": token})
            result = self.service.dispatch("create", params=data)
            self._ensure_token_consumed(token)
            self.assertTrue(result.get("store_cache", {}).get("customer"))

    def test_create_with_token_consumed(self):
        """
        Ensure a token can not be consumed twice
        :return:
        """
        self._enable_security_token()
        token = str(uuid4())
        with self._patch_get_new_token(forced_token=token):
            self.service.dispatch(
                "security_code_enabled", params=self.data.copy()
            )
            data = self.data.copy()
            data.update({"token": token})
            result = self.service.dispatch("create", params=data.copy())
            self._ensure_token_consumed(token)
            result.get("store_cache", {}).get("customer")
            with self.assertRaises(exceptions.UserError) as em:
                data = data.copy()
                data.update({"email": "new-customer@customer.example.com"})
                self.service.dispatch("create", params=data)
            self.assertIn("Invalid/Expired token", em.exception.name)
