# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from fastapi import status
from requests import Response

from odoo.tests.common import RecordCapturer, tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers import customer_router


@tagged("post_install", "-at_install")
class TestShopinvaderCustomerApi(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.Blacklist = cls.env["mail.blacklist"]
        cls.Lang = cls.env["res.lang"]

        cls.lang_en = cls.env.ref("base.lang_en")
        cls.lang_en.active = True
        cls.lang_fr = cls.env.ref("base.lang_fr")
        cls.lang_fr.active = True

        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
                "currency_id": cls.env.ref("base.EUR").id,
            }
        )
        cls.user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "email": "test@email",
            }
        )
        cls.test_partner = cls.user.partner_id
        cls.test_partner.write(
            {
                "phone": "12345",
                "property_product_pricelist": cls.pricelist.id,
                "lang": cls.lang_en.code,
            }
        )
        cls.default_fastapi_authenticated_partner = cls.test_partner
        cls.default_fastapi_router = customer_router

    def _call_test_client(self, url, **kwargs):
        method = kwargs.pop("method", "get")
        with self._create_test_client() as test_client:
            response: Response = getattr(test_client, method)(url, **kwargs)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        return response.json()

    def test_get_customer(self):
        customer = self._call_test_client("customer")
        partner = self.test_partner

        self.assertEqual(customer.get("name"), partner.name)
        self.assertEqual(customer.get("phone"), partner.phone)
        self.assertEqual(
            customer.get("pricelist_id"), partner.property_product_pricelist.id
        )
        self.assertEqual(
            customer.get("lang_id"),
            self.lang_en.id,
        )

    def test_update_customer(self):
        partner = self.test_partner
        data = {
            "mobile": "54321",
            "lang_id": self.lang_fr.id,
        }
        customer = self._call_test_client(
            "customer",
            json=data,
            method="post",
        )
        self.assertEqual(customer.get("mobile"), data.get("mobile"))
        self.assertEqual(partner.mobile, data.get("mobile"))
        self.assertEqual(partner.lang, "fr_FR")

    def test_update_customer_opt_in(self):
        partner = self.test_partner

        with RecordCapturer(self.Blacklist, [("email", "=", partner.email)]) as capture:
            self.assertFalse(capture.records)
            customer = self._call_test_client(
                "customer",
                json={
                    "opt_in": False,
                },
                method="post",
            )
            self.assertFalse(customer.get("opt_in"))
            self.assertTrue(partner.is_blacklisted)
            self.assertTrue(capture.records)
            customer = self._call_test_client(
                "customer",
                json={
                    "opt_in": True,
                },
                method="post",
            )
            self.assertTrue(customer.get("opt_in"))
            self.assertFalse(partner.is_blacklisted)
            self.assertFalse(capture.records)
