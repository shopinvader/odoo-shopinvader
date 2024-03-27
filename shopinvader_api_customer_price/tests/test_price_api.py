# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers.customer_price import customer_price_router


@tagged("post_install", "-at_install")
class TestCustomerPrice(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@test.eu",
            }
        )
        cls.pricelist1 = cls._create_price_list("Test Pricelist")
        cls.pricelist2 = cls._create_price_list("Test Pricelist")
        cls.products = cls.env["product.product"].browse()
        for i in range(1, 6):
            prod = cls.env["product.product"].create(
                {
                    "name": f"Test Product {i}",
                    "list_price": 10.0 * i,
                }
            )
            cls._create_price_list_item(cls.pricelist1, prod, prod.list_price - 2.0)
            cls._create_price_list_item(cls.pricelist2, prod, prod.list_price - 4.0)
            setattr(cls, f"prod{i}", prod)
            cls.products |= prod
        cls.default_fastapi_authenticated_partner = cls.partner
        cls.default_fastapi_router = customer_price_router

    @classmethod
    def _create_price_list(cls, name):
        return cls.env["product.pricelist"].create(
            {
                "name": name,
                "currency_id": cls.env.ref("base.USD").id,
                "company_id": cls.env.company.id,
            }
        )

    @classmethod
    def _create_price_list_item(
        cls, pricelist, product, price, date_start=None, date_end=None
    ):
        values = {
            "pricelist_id": pricelist.id,
            "applied_on": "0_product_variant",
            "base": "list_price",
            "compute_price": "fixed",
            "fixed_price": price,
            "product_id": product.id,
        }
        if date_start:
            values["date_start"] = date_start
        if date_end:
            values["date_end"] = date_end
        return cls.env["product.pricelist.item"].create(values)

    def test_get_none(self):
        data = {}
        with self._create_test_client() as test_client:
            response: Response = test_client.post("/customer_price", json=data)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_price_get_default(self):
        data = {"ids": self.products.ids}
        with self._create_test_client() as test_client:
            response: Response = test_client.post("/customer_price", json=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(len(res), 5)
        expected = (
            (self.prod1, 10.0),
            (self.prod2, 20.0),
            (self.prod3, 30.0),
            (self.prod4, 40.0),
            (self.prod5, 50.0),
        )
        for prod, price in expected:
            self.assertEqual(res[str(prod.id)]["value"], price)

    def test_price_get_customer_pricelist(self):
        self.partner.property_product_pricelist = self.pricelist2
        data = {"ids": self.products.ids}
        with self._create_test_client() as test_client:
            response: Response = test_client.post("/customer_price", json=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(len(res), 5)
        expected = (
            (self.prod1, 6.0),
            (self.prod2, 16.0),
            (self.prod3, 26.0),
            (self.prod4, 36.0),
            (self.prod5, 46.0),
        )
        for prod, price in expected:
            self.assertEqual(res[str(prod.id)]["value"], price)

    def test_price_get_custom_pricelist(self):
        data = {"ids": self.products.ids, "pricelist_id": self.pricelist1.id}
        with self._create_test_client() as test_client:
            response: Response = test_client.post("/customer_price", json=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(len(res), 5)
        expected = (
            (self.prod1, 8.0),
            (self.prod2, 18.0),
            (self.prod3, 28.0),
            (self.prod4, 38.0),
            (self.prod5, 48.0),
        )
        for prod, price in expected:
            self.assertEqual(res[str(prod.id)]["value"], price)
