# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import exceptions, fields

# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).

from functools import partial
from unittest import mock

from requests import Response

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from fastapi import status
from fastapi.testclient import TestClient

from .. import depends
from ..context import odoo_env_ctx
from ..models.fastapi_endpoint_demo import EndpointAppInfo, ExceptionType


class InvoiceServiceCase(TransactionCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.fastapi_demo_app = cls.env.ref("fastapi.fastapi_endpoint_demo")
        cls.app = cls.fastapi_demo_app._get_app()
        cls.app.dependency_overrides[depends.authenticated_partner_impl] = partial(
            lambda a: a, cls.test_partner
        )
        cls._ctx_token = odoo_env_ctx.set(
            cls.env(user=cls.env.ref("fastapi.my_demo_app_user"))
        )

    @classmethod
    def tearDownClass(cls) -> None:
        odoo_env_ctx.reset(cls._ctx_token)
        cls.fastapi_demo_app._reset_app()

        super().tearDownClass()

    def _get_path(self, path) -> str:
        return self.fastapi_demo_app.root_path + path

    def test_search_invoice(self) -> None:
        response: Response = self.client.get(self._get_path("/invoices"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(), {"Hello": "World"})


#class TestInvoiceServiceAnonymous(CommonInvoiceCase):
#    def setUp(self, *args, **kwargs):
#        super(TestInvoiceServiceAnonymous, self).setUp(*args, **kwargs)
#        self.partner = self.env.ref("base.res_partner_2").copy()
#
#    def test_get_invoice_anonymous(self):
#        """
#        Test the get on guest mode (using anonymous user).
#        It should not return any result, even if the anonymous user has some
#        invoices
#        :return:
#        """
#        # Check first without invoice related to the anonymous user
#        result = self.service_guest.dispatch("search")
#        data = result.get("data", [])
#        self.assertFalse(data)
#        # Then create a invoice related to the anonymous user
#        invoice = self._create_invoice(
#            partner=self.backend.anonymous_partner_id, validate=True
#        )
#        self.assertEqual(invoice.partner_id, self.backend.anonymous_partner_id)
#        result = self.service_guest.dispatch("search")
#        data = result.get("data", [])
#        self.assertFalse(data)
#        return
#
#    def _make_payment(self, invoice, journal=False, amount=False):
#        """
#        Make payment for given invoice
#        :param invoice: account.move recordset
#        :param amount: float
#        :return: bool
#        """
#        ctx = {"active_model": invoice._name, "active_ids": invoice.ids}
#        wizard_obj = self.register_payments_obj.with_context(**ctx)
#        register_payments = wizard_obj.create(
#            {
#                "payment_date": fields.Date.today(),
#                "journal_id": self.bank_journal_euro.id,
#                "payment_method_id": self.payment_method_manual_in.id,
#            }
#        )
#        values = {}
#        if journal:
#            values.update({"journal_id": journal.id})
#        if amount:
#            values.update({"amount": amount})
#        if values:
#            register_payments.write(values)
#        register_payments.create_payments()
#
#
#class TestInvoiceService(CommonInvoiceCase):
#    def test_get_invoice_logged(self):
#        """
#        Test the get on a logged user.
#        In the first part, the user should have any invoice.
#        But to the second, he should have one.
#        :return:
#        """
#        # Check first without invoice related to the partner
#        result = self.service.dispatch("search")
#        data = result.get("data", [])
#        self.assertFalse(data)
#        # Then create a invoice related to partner
#        invoice = self._confirm_and_invoice_sale(self.sale, payment=False)
#        self.assertEqual(invoice.partner_id, self.service.partner)
#        result = self.service.dispatch("search")
#        data = result.get("data", [])
#        # As the invoice is not paid, it shouldn't be into the data
#        self._check_data_content(data, self.invoice_obj.browse())
#        self._make_payment(invoice)
#        result = self.service.dispatch("search")
#        data = result.get("data", [])
#        self._check_data_content(data, invoice)
#        return
#
#    def test_get_invoice_no_number(self):
#        """
#        Test the get on an invoice without payment_reference ("number" into json result)
#        :return:
#        """
#        # Check first without invoice related to the partner
#        result = self.service.dispatch("search")
#        data = result.get("data", [])
#        self.assertFalse(data)
#        # Then create a invoice related to partner
#        invoice = self._confirm_and_invoice_sale(self.sale, payment=False)
#        self._make_payment(invoice)
#        invoice.write({"payment_reference": False})
#        result = self.service.dispatch("get", invoice.id)
#        data = result.get("data", [])
#        self.assertTrue(data.get("number"))
#        self.assertFalse(data.get("payment_reference"))
#
#    def test_get_invoice_no_date_due(self):
#        """
#        Test the get on an invoice without date_due ("date_due" into json result)
#        :return:
#        """
#        # Check first without invoice related to the partner
#        result = self.service.dispatch("search")
#        data = result.get("data", [])
#        self.assertFalse(data)
#        # Then create a invoice related to partner
#        invoice = self._confirm_and_invoice_sale(self.sale, payment=False)
#        self._make_payment(invoice)
#        invoice.write({"invoice_date_due": False})
#        result = self.service.dispatch("get", invoice.id)
#        data = result.get("data", [])
#        self.assertFalse(data.get("date_due"))
#
#    def test_get_multi_invoice(self):
#        """
#        Test the get on a logged user.
#        Check the search with many invoices
#        :return:
#        """
#        sale2 = self.sale.copy()
#        sale3 = self.sale.copy()
#        sale4 = self.sale.copy()
#        invoice1 = self._confirm_and_invoice_sale(self.sale)
#        invoice2 = self._confirm_and_invoice_sale(sale2)
#        invoice3 = self._confirm_and_invoice_sale(sale3)
#        invoice4 = self._confirm_and_invoice_sale(sale4)
#        invoices = invoice1 | invoice2 | invoice3 | invoice4
#        self.assertEqual(invoice1.partner_id, self.service.partner)
#        self.assertEqual(invoice2.partner_id, self.service.partner)
#        self.assertEqual(invoice3.partner_id, self.service.partner)
#        self.assertEqual(invoice4.partner_id, self.service.partner)
#        result = self.service.dispatch("search")
#        data = result.get("data", [])
#        self._check_data_content(data, invoices)
#        return
#
#    def test_invoice_get(self):
#        """
#        Test the invoice/get on a logged user.
#        Create many invoices to ensure the result will be the one of given id.
#        :return:
#        """
#        sale2 = self.sale.copy()
#        sale3 = self.sale.copy()
#        sale4 = self.sale.copy()
#        invoice1 = self._confirm_and_invoice_sale(self.sale)
#        invoice2 = self._confirm_and_invoice_sale(sale2)
#        invoice3 = self._confirm_and_invoice_sale(sale3)
#        invoice4 = self._confirm_and_invoice_sale(sale4)
#        self.assertEqual(invoice1.partner_id, self.service.partner)
#        self.assertEqual(invoice2.partner_id, self.service.partner)
#        self.assertEqual(invoice3.partner_id, self.service.partner)
#        self.assertEqual(invoice4.partner_id, self.service.partner)
#        result = self.service.dispatch("get", invoice1.id)
#        data = result.get("data", [])
#        self._check_data_content([data], invoice1)
#        return
#
#    def test_invoice_get_not_owner(self):
#        """
#        Test the invoice/get on a logged user.
#        For this case, the logged user is not the owner of these invoices.
#        So we should have an exception.
#        :return:
#        """
#        invoice1 = self._confirm_and_invoice_sale(self.sale)
#        self.assertEqual(invoice1.partner_id, self.service.partner)
#        # The owner can do a 'get' on it
#        self.service.dispatch("get", invoice1.id)
#        # Now use another user/partner
#        with self.work_on_services(partner=self.partner2) as work:
#            self.service = work.component(usage="invoices")
#        with self.assertRaises(exceptions.MissingError) as cm:
#            self.service.dispatch("get", invoice1.id)
#        self.assertIn("does not exist", cm.exception.args[0])
#        self.assertIn(str(invoice1.id), cm.exception.args[0])
#        return
