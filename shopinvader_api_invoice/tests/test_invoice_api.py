# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.shopinvader_schema_invoice.tests.common import (
    InvoiceCaseMixin,
    create_invoice,
)

from ..routers import invoice_router


@tagged("post_install", "-at_install")
class TestInvoice(FastAPITransactionCase, InvoiceCaseMixin):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls._setup_invoice_data()
        cls.default_fastapi_authenticated_partner = cls.partner
        cls.default_fastapi_router = invoice_router

    def _create_invoice(self, **kw):
        return create_invoice(
            self.env, self.partner, self.product, account=self.account_receivable, **kw
        )

    def test_search_invoices_none(self):
        with self._create_test_client() as test_client:
            response: Response = test_client.get("/invoices")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

    def test_search_invoices_not_ready(self):
        for __ in range(3):
            self._create_invoice()
        with self._create_test_client() as test_client:
            response: Response = test_client.get("/invoices")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # still zero because state is not ok
        self.assertEqual(response.json()["count"], 0)

    def test_search_invoices_ok(self):
        for i in range(3):
            self._create_invoice(validate=i != 2)
        with self._create_test_client() as test_client:
            response: Response = test_client.get("/invoices")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2 validated out of 3
        self.assertEqual(response.json()["count"], 2)

    def test_download(self):
        inv1 = self._create_invoice()
        with self._create_test_client() as test_client:
            response: Response = test_client.get(f"/invoices/{inv1.id}/download")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        inv2 = self._create_invoice()
        with self._create_test_client() as test_client:
            response: Response = test_client.get(f"/invoices/{inv2.id}/download")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
