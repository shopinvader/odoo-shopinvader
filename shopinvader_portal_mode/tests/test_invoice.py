# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from .common import PortalModeCommonCase


class TestInvoiceService(PortalModeCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for sale in cls.shop_sales + cls.non_shop_sales:
            cls._invoice_sale(sale)
        payment_method = cls.env.ref(
            "account.account_payment_method_manual_in"
        )
        journal = cls.env["account.journal"].create(
            {"name": "Bank", "type": "bank", "code": "BNK627"}
        )
        cls.all_invoices = (cls.shop_sales + cls.non_shop_sales).invoice_ids
        for inv in cls.all_invoices:
            cls._make_payment(inv, journal, payment_method)

    @staticmethod
    def _invoice_sale(sale):
        for line in sale.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        return sale._create_invoices()

    @staticmethod
    def _make_payment(invoice, journal, payment_method):
        """
        Make the invoice payment
        :param invoice: account.invoice recordset
        :return: bool
        """
        payment_wiz = invoice.env["account.payment.register"]
        if invoice.state != "posted":
            invoice.post()
        ctx = {"active_ids": invoice.ids}
        wizard_obj = payment_wiz.with_context(ctx)
        register_payments = wizard_obj.create(
            {
                "payment_date": fields.Date.today(),
                "journal_id": journal.id,
                "payment_method_id": payment_method.id,
            }
        )
        register_payments.create_payments()

    def test_invoice_domain_default(self):
        service = self._get_service("invoice")
        domain = service._get_base_search_domain()
        invoices = self.env["account.move"].search(domain)
        self.assertEqual(
            sorted(invoices.ids), sorted(self.shop_sales.invoice_ids.ids)
        )

    def test_invoice_domain_portal_mode(self):
        self.backend.sale_order_portal_mode = True
        service = self._get_service("invoice")
        domain = service._get_base_search_domain()
        invoices = self.env["account.move"].search(domain)
        self.assertEqual(sorted(invoices.ids), sorted(self.all_invoices.ids))
