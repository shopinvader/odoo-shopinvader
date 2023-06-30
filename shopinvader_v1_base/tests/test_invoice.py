# Copyright 2019 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import CommonCase, CommonTestDownload


class TestInvoice(CommonCase, CommonTestDownload):
    @classmethod
    def setUpClass(cls):
        super(TestInvoice, cls).setUpClass()
        cls.register_payments_obj = cls.env["account.payment.register"]
        cls.journal_obj = cls.env["account.journal"]
        cls.sale = cls.env.ref("shopinvader.sale_order_2")
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.payment_method_manual_in = cls.env.ref(
            "account.account_payment_method_manual_in"
        )
        cls.bank_journal_euro = cls.journal_obj.create(
            {"name": "Bank", "type": "bank", "code": "BNK627"}
        )
        cls.invoice_obj = cls.env["account.move"]
        cls.invoice = cls._confirm_and_invoice_sale(cls, cls.sale)
        cls.non_sale_invoice = cls.invoice.copy()
        # set the layout on the company to be sure that the print action
        # will not display the document layout configurator
        cls.env.company.external_report_layout_id = cls.env.ref(
            "web.external_layout_standard"
        ).id

    def setUp(self, *args, **kwargs):
        super(TestInvoice, self).setUp(*args, **kwargs)
        with self.work_on_services(partner=self.partner) as work:
            self.sale_service = work.component(usage="sales")
            self.invoice_service = work.component(usage="invoices")

    def _confirm_and_invoice_sale(self, sale):
        sale.action_confirm()
        for line in sale.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        return sale._create_invoices()

    def _create_invoice(self, partner, **kw):
        product = self.env.ref("product.product_product_4")
        account = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        values = {
            "partner_id": self.partner.id,
            "type": "out_invoice",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": account.id,
                        "product_id": product.product_variant_ids[:1].id,
                        "name": "Product 1",
                        "quantity": 4.0,
                        "price_unit": 123.00,
                    },
                )
            ],
        }
        values.update(kw)
        return self.env["account.move"].create(values)

    def test_01(self):
        """
        Data
            * A confirmed sale order with an invoice not yet paid
        Case:
            * Try to download the PDF
        Expected result:
            * MissingError should be raised
        """
        self._test_download_not_allowed(self.invoice_service, self.invoice)

    def test_02(self):
        """
        Data
            * A confirmed sale order with a paid invoice
        Case:
            * Try to download the PDF
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
            * Try to download the PDF
        Expected result:
            * MissingError should be raised
        """
        sale = self.env.ref("sale.sale_order_1")
        sale.shopinvader_backend_id = self.backend
        self.assertNotEqual(sale.partner_id, self.partner)
        invoice = self._confirm_and_invoice_sale(sale)
        self._make_payment(invoice)
        self._test_download_not_owner(self.invoice_service, self.invoice)

    def test_domain_01(self):
        # By default include only invoices related to sales
        self.assertTrue(self.backend.invoice_linked_to_sale_only)
        # and only paid invoice are accessible
        self.assertFalse(self.backend.invoice_access_open)
        # Invoices are open, none of them is included
        self._ensure_posted(self.invoice)
        self._ensure_posted(self.non_sale_invoice)
        domain = self.invoice_service._get_base_search_domain()
        self.assertNotIn(self.non_sale_invoice, self.invoice_obj.search(domain))
        self.assertNotIn(self.invoice, self.invoice_obj.search(domain))
        # pay both invoices
        self._make_payment(self.invoice)
        self._make_payment(self.non_sale_invoice)
        domain = self.invoice_service._get_base_search_domain()
        # Extra invoice still not found
        self.assertNotIn(self.non_sale_invoice, self.invoice_obj.search(domain))
        self.assertIn(self.invoice, self.invoice_obj.search(domain))

    def test_domain_02(self):
        # Include extra invoices
        self.backend.invoice_linked_to_sale_only = False
        # and only paid invoice are accessible
        self.assertFalse(self.backend.invoice_access_open)
        # Invoices are open, none of them is included
        self._ensure_posted(self.invoice)
        self._ensure_posted(self.non_sale_invoice)
        domain = self.invoice_service._get_base_search_domain()
        self.assertNotIn(self.non_sale_invoice, self.invoice_obj.search(domain))
        self.assertNotIn(self.invoice, self.invoice_obj.search(domain))
        # pay both invoices
        self._make_payment(self.invoice)
        self._make_payment(self.non_sale_invoice)
        domain = self.invoice_service._get_base_search_domain()
        # Extra invoice available now as well
        self.assertIn(self.non_sale_invoice, self.invoice_obj.search(domain))
        self.assertIn(self.invoice, self.invoice_obj.search(domain))

    def test_domain_03(self):
        # Include extra invoices
        self.backend.invoice_linked_to_sale_only = False
        # and open invoices enabled as well
        self.backend.invoice_access_open = True
        self._ensure_posted(self.invoice)
        self._ensure_posted(self.non_sale_invoice)
        domain = self.invoice_service._get_base_search_domain()
        self.assertIn(self.non_sale_invoice, self.invoice_obj.search(domain))
        self.assertIn(self.invoice, self.invoice_obj.search(domain))
        # pay both invoices
        self._make_payment(self.invoice)
        self._make_payment(self.non_sale_invoice)
        domain = self.invoice_service._get_base_search_domain()
        # Still both available
        self.assertIn(self.non_sale_invoice, self.invoice_obj.search(domain))
        self.assertIn(self.invoice, self.invoice_obj.search(domain))

    def test_report_get(self):
        default_report = self.env.ref("account.account_invoices")
        self.assertEqual(
            self.invoice_service._get_report_action(self.invoice),
            default_report.report_action(self.invoice, config=False),
        )
        # set a custom report
        custom = default_report.copy({"name": "My custom report"})
        self.backend.invoice_report_id = custom
        self.assertEqual(
            self.invoice_service._get_report_action(self.invoice)["name"],
            "My custom report",
        )


class DeprecatedTestInvoice(TestInvoice):
    def setUp(self, *args, **kwargs):
        super(DeprecatedTestInvoice, self).setUp(*args, **kwargs)
        with self.work_on_services(partner=self.partner) as work:
            self.invoice_service = work.component(usage="invoice")
