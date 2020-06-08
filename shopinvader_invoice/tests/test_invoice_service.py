# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import exceptions, fields

from .common import CommonInvoiceCase


class TestInvoiceServiceAnonymous(CommonInvoiceCase):
    def setUp(self, *args, **kwargs):
        super(TestInvoiceServiceAnonymous, self).setUp(*args, **kwargs)
        self.partner = self.env.ref("base.res_partner_2").copy()

    def test_get_invoice_anonymous(self):
        """
        Test the get on guest mode (using anonymous user).
        It should not return any result, even if the anonymous user has some
        invoices
        :return:
        """
        # Check first without invoice related to the anonymous user
        result = self.service_guest.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        # Then create a invoice related to the anonymous user
        invoice = self._create_invoice(
            partner=self.backend.anonymous_partner_id, validate=True
        )
        self.assertEquals(
            invoice.partner_id, self.backend.anonymous_partner_id
        )
        result = self.service_guest.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        return

    def _make_payment(self, invoice, journal=False, amount=False):
        """
        Make payment for given invoice
        :param invoice: account.invoice recordset
        :param amount: float
        :return: bool
        """
        ctx = {"active_model": invoice._name, "active_ids": invoice.ids}
        wizard_obj = self.register_payments_obj.with_context(**ctx)
        register_payments = wizard_obj.create(
            {
                "payment_date": fields.Date.today(),
                "journal_id": self.bank_journal_euro.id,
                "payment_method_id": self.payment_method_manual_in.id,
            }
        )
        values = {}
        if journal:
            values.update({"journal_id": journal.id})
        if amount:
            values.update({"amount": amount})
        if values:
            register_payments.write(values)
        register_payments.create_payment()


class TestInvoiceService(CommonInvoiceCase):
    def test_get_invoice_logged(self):
        """
        Test the get on a logged user.
        In the first part, the user should have any invoice.
        But to the second, he should have one.
        :return:
        """
        # Check first without invoice related to the partner
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        # Then create a invoice related to partner
        invoice = self._confirm_and_invoice_sale(self.sale, payment=False)
        self.assertEquals(invoice.partner_id, self.service.partner)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        # As the invoice is not paid, it shouldn't be into the data
        self._check_data_content(data, self.invoice_obj.browse())
        self._make_payment(invoice)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, invoice)
        return

    def test_get_multi_invoice(self):
        """
        Test the get on a logged user.
        Check the search with many invoices
        :return:
        """
        sale2 = self.sale.copy()
        sale3 = self.sale.copy()
        sale4 = self.sale.copy()
        invoice1 = self._confirm_and_invoice_sale(self.sale)
        invoice2 = self._confirm_and_invoice_sale(sale2)
        invoice3 = self._confirm_and_invoice_sale(sale3)
        invoice4 = self._confirm_and_invoice_sale(sale4)
        invoices = invoice1 | invoice2 | invoice3 | invoice4
        self.assertEquals(invoice1.partner_id, self.service.partner)
        self.assertEquals(invoice2.partner_id, self.service.partner)
        self.assertEquals(invoice3.partner_id, self.service.partner)
        self.assertEquals(invoice4.partner_id, self.service.partner)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, invoices)
        return

    def test_invoice_get(self):
        """
        Test the invoice/get on a logged user.
        Create many invoices to ensure the result will be the one of given id.
        :return:
        """
        sale2 = self.sale.copy()
        sale3 = self.sale.copy()
        sale4 = self.sale.copy()
        invoice1 = self._confirm_and_invoice_sale(self.sale)
        invoice2 = self._confirm_and_invoice_sale(sale2)
        invoice3 = self._confirm_and_invoice_sale(sale3)
        invoice4 = self._confirm_and_invoice_sale(sale4)
        self.assertEquals(invoice1.partner_id, self.service.partner)
        self.assertEquals(invoice2.partner_id, self.service.partner)
        self.assertEquals(invoice3.partner_id, self.service.partner)
        self.assertEquals(invoice4.partner_id, self.service.partner)
        result = self.service.dispatch("get", _id=invoice1.id)
        data = result.get("data", [])
        self._check_data_content([data], invoice1)
        return

    def test_invoice_get_not_owner(self):
        """
        Test the invoice/get on a logged user.
        For this case, the logged user is not the owner of these invoices.
        So we should have an exception.
        :return:
        """
        invoice1 = self._confirm_and_invoice_sale(self.sale)
        self.assertEquals(invoice1.partner_id, self.service.partner)
        # The owner can do a 'get' on it
        self.service.dispatch("get", _id=invoice1.id)
        # Now use another user/partner
        with self.work_on_services(partner=self.partner2) as work:
            self.service = work.component(usage="invoices")
        with self.assertRaises(exceptions.MissingError) as cm:
            self.service.dispatch("get", _id=invoice1.id)
        self.assertIn("does not exist", cm.exception.name)
        self.assertIn(str(invoice1.id), cm.exception.name)
        return
