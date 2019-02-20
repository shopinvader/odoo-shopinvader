# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase
from odoo.exceptions import MissingError
from odoo import fields


class SaleCase(CommonCase):

    def setUp(self, *args, **kwargs):
        super(SaleCase, self).setUp(*args, **kwargs)
        self.sale = self.env.ref('shopinvader.sale_order_2')
        self.partner = self.env.ref('shopinvader.partner_1')
        with self.work_on_services(
                partner=self.partner) as work:
            self.service = work.component(usage='sales')

    def test_read_sale(self):
        self.sale.action_confirm_cart()
        res = self.service.get(self.sale.id)
        self.assertEqual(res['id'], self.sale.id)
        self.assertEqual(res['name'], self.sale.name)

    def test_cart_are_not_readable_as_sale(self):
        with self.assertRaises(MissingError):
            self.service.get(self.sale.id)

    def test_list_sale(self):
        self.sale.action_confirm_cart()
        res = self.service.search()
        self.assertEqual(len(res['data']), 1)
        sale = res['data'][0]
        self.assertEqual(sale['id'], self.sale.id)
        self.assertEqual(sale['name'], self.sale.name)

    def test_hack_read_other_customer_sale(self):
        sale = self.env.ref('sale.sale_order_1')
        sale.shopinvader_backend_id = self.backend
        # We raise a not found error because in a point of view of the hacker
        # and his right the record does not exist
        with self.assertRaises(MissingError):
            self.service.get(sale.id)

    def _create_notification_config(self):
        template = self.env.ref("account.email_template_edi_invoice")
        values = {
            'model_id': self.env.ref("account.model_account_invoice").id,
            'notification_type': 'invoice_send_email',
            'template_id': template.id,
        }
        self.service.shopinvader_backend.notification_ids.unlink()
        self.service.shopinvader_backend.write({
            'notification_ids': [
                (0, 0, values),
            ],
        })

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
            line.write({
                'qty_delivered': line.product_uom_qty,
            })
        invoice_id = self.sale.action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_id)
        description = "Notify %s for %s,%s" % (
            notif, invoice._name, invoice.id)
        domain = [
            ('name', '=', description),
            ('date_created', '>=', now),
        ]
        self.service.dispatch('ask_email_invoice', _id=self.sale.id)
        self.assertEquals(self.env['queue.job'].search_count(domain), 1)
