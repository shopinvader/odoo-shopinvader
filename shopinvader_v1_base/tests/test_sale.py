# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.exceptions import MissingError
from odoo.tools import mute_logger

from .common import CommonCase, CommonTestDownload


class CommonSaleCase(CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("shopinvader.sale_order_2")
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.register_payments_obj = cls.env["account.payment.register"]
        cls.journal_obj = cls.env["account.journal"]
        cls.payment_method_manual_in = cls.env.ref(
            "account.account_payment_method_manual_in"
        )
        cls.bank_journal_euro = cls.journal_obj.create(
            {"name": "Bank", "type": "bank", "code": "BNK6278"}
        )

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="sales")


class SaleCase(CommonSaleCase, CommonTestDownload):
    def _confirm_and_invoice_sale(self):
        self.sale.action_confirm()
        for line in self.sale.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        self.invoice = self.sale._create_invoices()

    def test_read_sale(self):
        self.sale.action_confirm_cart()
        res = self.service.get(self.sale.id)
        self.assertEqual(res["id"], self.sale.id)
        self.assertEqual(res["name"], self.sale.name)
        self.assertEqual(res["state"], self.sale.shopinvader_state)
        self.assertEqual(
            res["state_label"],
            self._get_selection_label(self.sale, "shopinvader_state"),
        )

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
        self.assertEqual(sale["state"], self.sale.shopinvader_state)
        state_label = self._get_selection_label(self.sale, "shopinvader_state")
        self.assertEqual(sale["state_label"], state_label)
        self.assertEqual(sale["client_order_ref"], "DEMO_ORDER_2")

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
            "model_id": self.env.ref("account.model_account_move").id,
            "notification_type": "invoice_send_email",
            "template_id": template.id,
        }
        self.service.shopinvader_backend.notification_ids.unlink()
        self.service.shopinvader_backend.write({"notification_ids": [(0, 0, values)]})

    @mute_logger("odoo.models.unlink")
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
        invoice = self.sale._create_invoices()
        description = "Notify {} for {},{}".format(notif, invoice._name, invoice.id)
        domain = [("name", "=", description), ("date_created", ">=", now)]
        self.service.dispatch("ask_email_invoice", self.sale.id)
        self.assertEqual(self.env["queue.job"].search_count(domain), 1)

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
        self.assertNotEqual(self.invoice.payment_state, "paid")
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
        self.assertEqual(self.invoice.payment_state, "paid")
        res = self.service.get(self.sale.id)
        self.assertTrue(res)
        self.assertEqual(
            res["invoices"],
            [
                {
                    "id": self.invoice.id,
                    "name": self.invoice.name,
                    "date": self.invoice.invoice_date,
                }
            ],
        )

    def test_download01(self):
        """
        Data
            * A draft sale order
        Case:
            * Try to download the document
        Expected result:
            * MissingError should be raised
        """
        self._test_download_not_allowed(self.service, self.sale)

    def test_download02(self):
        """
        Data
            * A confirmed sale order
        Case:
            * Try to download the document
        Expected result:
            * An http response with the file to download
        """
        self.sale.action_confirm_cart()
        self._test_download_allowed(self.service, self.sale)

    def test_download03(self):
        """
        Data
            * A confirmed sale order but not for the current customer
        Case:
            * Try to download the document
        Expected result:
            * MissingError should be raised
        """
        sale = self.env.ref("sale.sale_order_1")
        sale.action_confirm_cart()
        sale.shopinvader_backend_id = self.backend
        self.assertNotEqual(sale.partner_id, self.service.partner)
        self._test_download_not_owner(self.service, sale)

    # TODO (long-term): this test is not specifically for sale.order.
    # This as many other tests should be moved to a generic test case
    # to ensure core feature a working on independently.
    def test_sale_search_order(self):
        order1 = self.sale
        order1.date_order = "2020-08-18"
        order1.action_confirm_cart()
        order2 = order1.copy({"date_order": "2020-08-31"})
        order2.action_confirm_cart()
        res = self.service.search()
        self.assertEqual(len(res["data"]), 2)
        # by default order is `_order = 'date_order desc, id desc'`
        self.assertEqual(res["data"][0]["id"], order2.id)
        self.assertEqual(res["data"][1]["id"], order1.id)
        # change ordering
        res = self.service.dispatch("search", params={"order": "date_order asc"})
        self.assertEqual(len(res["data"]), 2)
        self.assertEqual(res["data"][0]["id"], order1.id)
        self.assertEqual(res["data"][1]["id"], order2.id)
        order1.name = "O1"
        order2.name = "O2"
        res = self.service.dispatch("search", params={"order": "name desc"})
        self.assertEqual(len(res["data"]), 2)
        self.assertEqual(res["data"][0]["id"], order2.id)
        self.assertEqual(res["data"][1]["id"], order1.id)
