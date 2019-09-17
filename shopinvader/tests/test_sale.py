# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import MissingError

from .common import CommonCase


class SaleCase(CommonCase):
    def setUp(self, *args, **kwargs):
        super(SaleCase, self).setUp(*args, **kwargs)
        self.sale = self.env.ref("shopinvader.sale_order_2")
        self.partner = self.env.ref("shopinvader.partner_1")
        self.register_payments_obj = self.env["account.register.payments"]
        self.journal_obj = self.env["account.journal"]
        self.payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in"
        )
        self.bank_journal_euro = self.journal_obj.create(
            {"name": "Bank", "type": "bank", "code": "BNK6278"}
        )
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="sales")

    def _confirm_and_invoice_sale(self):
        self.sale.action_confirm()
        for line in self.sale.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        invoice_id = self.sale.action_invoice_create()
        self.invoice = self.env["account.invoice"].browse(invoice_id)
        self.invoice.action_invoice_open()
        self.invoice.action_move_create()

    def test_read_sale(self):
        self.sale.action_confirm_cart()
        res = self.service.get(self.sale.id)
        self.assertEqual(res["id"], self.sale.id)
        self.assertEqual(res["name"], self.sale.name)

    def test_cart_are_not_readable_as_sale(self):
        with self.assertRaises(MissingError):
            self.service.get(self.sale.id)

    def test_list_sale(self):
        self.sale.action_confirm_cart()
        res = self.service.search()
        self.assertEqual(len(res["data"]), 1)
        sale = res["data"][0]
        self.assertEqual(sale["id"], self.sale.id)
        self.assertEqual(sale["name"], self.sale.name)

    def test_hack_read_other_customer_sale(self):
        sale = self.env.ref("sale.sale_order_1")
        sale.shopinvader_backend_id = self.backend
        # We raise a not found error because in a point of view of the hacker
        # and his right the record does not exist
        with self.assertRaises(MissingError):
            self.service.get(sale.id)

    def _create_notification_config(self):
        template = self.env.ref("account.email_template_edi_invoice")
        values = {
            "model_id": self.env.ref("account.model_account_invoice").id,
            "notification_type": "invoice_send_email",
            "template_id": template.id,
        }
        self.service.shopinvader_backend.notification_ids.unlink()
        self.service.shopinvader_backend.write(
            {"notification_ids": [(0, 0, values)]}
        )

    def test_ask_email_invoice(self):
        """
        Test the ask_email when not logged.
        As the user is not logged, no email should be created
        :return:
        """
        self._create_notification_config()
        now = fields.Date.today()
        notif = "invoice_send_email"
        self.sale.action_confirm()
        for line in self.sale.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        invoice_id = self.sale.action_invoice_create()
        invoice = self.env["account.invoice"].browse(invoice_id)
        description = "Notify {} for {},{}".format(
            notif, invoice._name, invoice.id
        )
        domain = [("name", "=", description), ("date_created", ">=", now)]
        self.service.dispatch("ask_email_invoice", _id=self.sale.id)
        self.assertEquals(self.env["queue.job"].search_count(domain), 1)

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

    def test_invoice_01(self):
        """
        Data
            * A confirmed sale order with an invoice not yet paid
        Case:
            * Load data
        Expected result:
            * No invoice information returned
        """
        self._confirm_and_invoice_sale()
        self.assertNotEqual(self.invoice.state, "paid")
        res = self.service.get(self.sale.id)
        self.assertFalse(res["invoices"])

    def test_invoice_02(self):
        """
        Data
            * A confirmed sale order with a paid invoice
        Case:
            * Load data
        Expected result:
            * Invoice information must be filled
        """
        self._confirm_and_invoice_sale()
        self._make_payment(self.invoice)
        self.assertEqual(self.invoice.state, "paid")
        res = self.service.get(self.sale.id)
        self.assertTrue(res)
        self.assertEqual(
            res["invoices"],
            [
                {
                    "id": self.invoice.id,
                    "name": self.invoice.number,
                    "date": self.invoice.date_invoice,
                }
            ],
        )
