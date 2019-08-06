# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import mock
from odoo.exceptions import MissingError

from .common import CommonCase


class TestInvoice(CommonCase):
    def setUp(self, *args, **kwargs):
        super(TestInvoice, self).setUp(*args, **kwargs)
        self.sale = self.env.ref("shopinvader.sale_order_2")
        self.partner = self.env.ref("shopinvader.partner_1")
        with self.work_on_services(partner=self.partner) as work:
            self.sale_service = work.component(usage="sales")
            self.invoice_service = work.component(usage="invoice")
        self.invoice = self._confirm_and_invoice_sale(self.sale)

    def _confirm_and_invoice_sale(self, sale):
        sale.action_confirm()
        for line in sale.order_line:
            line.write({"qty_delivered": line.product_uom_qty})
        invoice_id = sale.action_invoice_create()
        invoice = self.env["account.invoice"].browse(invoice_id)
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
        with self.assertRaises(MissingError):
            self.invoice_service.download(self.invoice.id)

    def test_02(self):
        """
        Data
            * A confirmed sale order with a paid invoice
        Case:
            * Try to download the image
        Expected result:
            * An http response with the file to download
        """
        self.invoice.confirm_paid()
        with mock.patch(
            "openerp.addons.shopinvader.services.invoice.content_disposition"
        ) as mocked_cd, mock.patch(
            "openerp.addons.shopinvader.services.invoice.request"
        ) as mocked_request:
            mocked_cd.return_value = "attachment; filename=test"
            make_response = mock.MagicMock()
            mocked_request.make_response = make_response
            self.invoice_service.download(self.invoice.id)
            self.assertEqual(1, make_response.call_count)
            content, headers = make_response.call_args[0]
            self.assertTrue(content)
            self.assertIn(
                ("Content-Disposition", "attachment; filename=test"), headers
            )

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
        invoice.confirm_paid()
        with self.assertRaises(MissingError):
            self.invoice_service.download(invoice.id)
