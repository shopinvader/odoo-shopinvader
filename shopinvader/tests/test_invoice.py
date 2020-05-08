# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields

from .common import CommonCase, CommonTestDownload


class TestInvoice(CommonCase, CommonTestDownload):
    def setUp(self, *args, **kwargs):
        super(TestInvoice, self).setUp(*args, **kwargs)
        self.register_payments_obj = self.env["account.register.payments"]
        self.journal_obj = self.env["account.journal"]
        self.sale = self.env.ref("shopinvader.sale_order_2")
        self.partner = self.env.ref("shopinvader.partner_1")
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )
        self.bank_journal_euro = self.journal_obj.create(
            {"name": "Bank", "type": "bank", "code": "BNK627"}
        )
        with self.work_on_services(partner=self.partner) as work:
            self.sale_service = work.component(usage="sales")
            self.invoice_service = work.component(usage="invoices")
        self.invoice = self._confirm_and_invoice_sale(self.sale)

    def _make_payment(self, invoice):
        """
        Make the invoice payment
        :param invoice: account.invoice recordset
        :return: bool
        """
        ctx = {"active_model": invoice._name, "active_ids": invoice.ids}
        wizard_obj = self.register_payments_obj.with_context(ctx)
        register_payments = wizard_obj.create(
            {
                "payment_date": fields.Date.today(),
                "journal_id": self.bank_journal_euro.id,
                "payment_method_id": self.payment_method_manual_in.id,
            }
        )
        register_payments.create_payment()

    def _confirm_and_invoice_sale(self, sale):
        sale.action_confirm()
        for line in sale.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        invoice_id = sale.action_invoice_create()
        invoice = self.env["account.invoice"].browse(invoice_id)
        invoice.action_invoice_open()
        invoice.action_move_create()
        return invoice

    def test_01(self):
        """
        Data
            * A confirmed sale order with an invoice not yet paid
        Case:
            * Try to download the image
        Expected result:
            * MissingError should be raised
        """
        self._test_download_not_allowed(self.invoice_service, self.invoice)

    def test_02(self):
        """
        Data
            * A confirmed sale order with a paid invoice
        Case:
            * Try to download the image
        Expected result:
            * An http response with the file to download
        """
        self._make_payment(self.invoice)
        self._test_download_allowed(self.invoice_service, self.invoice)

    def test_03(self):
        """
        Data
            * A confirmed sale order with a paid invoice but not for the
            current customer
        Case:
            * Try to download the image
        Expected result:
            * MissingError should be raised
        """
        sale = self.env.ref("sale.sale_order_1")
        sale.shopinvader_backend_id = self.backend
        self.assertNotEqual(sale.partner_id, self.partner)
        invoice = self._confirm_and_invoice_sale(sale)
        self._make_payment(invoice)
        self._test_download_not_owner(self.invoice_service, self.invoice)


class DeprecatedTestInvoice(TestInvoice):
    def setUp(self, *args, **kwargs):
        super(DeprecatedTestInvoice, self).setUp(*args, **kwargs)
        with self.work_on_services(partner=self.partner) as work:
            self.invoice_service = work.component(usage="invoice")
