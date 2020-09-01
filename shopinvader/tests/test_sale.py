# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import fields
from odoo.exceptions import MissingError

from .common import CommonCase, CommonTestDownload


class SaleCase(CommonCase, CommonTestDownload):
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
        register_payments.create_payments()

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

    def _create_sale_order(self):
        """
        Create a new sale.order with 1 line.
        :return: bool
        """
        self.sale = sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "partner_shipping_id": self.partner.id,
                "partner_invoice_id": self.partner.id,
                "pricelist_id": self.backend.pricelist_id.id,
                "typology": "cart",
                "shopinvader_backend_id": self.backend.id,
                "date_order": fields.Datetime.now(),
                "project_id": self.backend.account_analytic_id.id,
            }
        )
        so_line_obj = self.env["sale.order.line"]
        line_values = {
            "order_id": sale.id,
            "product_id": self.product_1.id,
            "product_uom_qty": 1,
        }
        new_line_values = so_line_obj.play_onchanges(
            line_values, line_values.keys()
        )
        new_line_values.update(line_values)
        self.line = so_line_obj.create(new_line_values)
        return True

    def test_update_pricelist(self):
        """
        Cases to test:
        - A pricelist is defined on the backend (applied on the SO)
            => Then change the pricelist (check new price applied)
        - No pricelist defined on the backend (so the default comes from partner)
            => Then define a pricelist on the backend (check applied)
        - Pricelist on the backend (applied on SO)
            => Then remove it (check pricelist from partner is applied)
        :return:
        """
        # Let the user to set some discount if necessary
        self.env.ref("sale.group_discount_per_so_line").write(
            {"users": [(4, self.env.user.id, False)]}
        )
        fixed_price = 650
        reduction = -100
        self._create_pricelists(fixed_price, reduction)
        self._create_sale_order()
        self.assertEqual(self.backend.pricelist_id, self.sale.pricelist_id)
        self.backend.write({"pricelist_id": self.first_pricelist.id})
        self.sale._update_pricelist_and_update_line_prices()
        self.assertEqual(self.first_pricelist, self.sale.pricelist_id)
        self.assertAlmostEqual(
            self.line.price_unit, fixed_price, places=self.precision
        )
        self.backend.write({"pricelist_id": self.second_pricelist.id})
        self.sale._update_pricelist_and_update_line_prices()
        self.assertEqual(self.second_pricelist, self.sale.pricelist_id)
        self.assertAlmostEqual(
            self.line.price_unit,
            fixed_price + reduction,
            places=self.precision,
        )

    def _create_pricelists(self, fixed_price, reduction):
        """
        Create 2 new pricelists (one with a fixed price) and another
        (based on the first) with the given reduction.
        :param fixed_price: float
        :param reduction: float
        :return: bool
        """
        pricelist_values = {
            "name": "Custom pricelist 1",
            "discount_policy": "with_discount",
            "item_ids": [
                (
                    0,
                    0,
                    {
                        "applied_on": "1_product",
                        "product_tmpl_id": self.product_1.product_tmpl_id.id,
                        "compute_price": "fixed",
                        "fixed_price": fixed_price,
                    },
                )
            ],
        }
        self.first_pricelist = self.env["product.pricelist"].create(
            pricelist_values
        )
        pricelist_values = {
            "name": "Custom pricelist 2",
            "discount_policy": "with_discount",
            "item_ids": [
                (
                    0,
                    0,
                    {
                        "applied_on": "1_product",
                        "product_tmpl_id": self.product_1.product_tmpl_id.id,
                        "compute_price": "formula",
                        "base": "pricelist",
                        "price_surcharge": reduction,
                        "base_pricelist_id": self.first_pricelist.id,
                        "date_start": fields.Date.today(),
                        # TODO: remove timedelta after Odoo date bug
                        # https://github.com/odoo/odoo/pull/51967
                        "date_end": fields.Date.today() + timedelta(days=1),
                    },
                )
            ],
        }
        self.second_pricelist = self.env["product.pricelist"].create(
            pricelist_values
        )
        return True

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
