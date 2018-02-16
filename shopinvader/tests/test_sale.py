# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonCase
from werkzeug.exceptions import NotFound


class SaleCase(CommonCase):

    def setUp(self, *args, **kwargs):
        super(SaleCase, self).setUp(*args, **kwargs)
        self.sale = self.env.ref('shopinvader.sale_order_2')
        self.partner = self.env.ref('shopinvader.partner_1')
        with self.work_on_services(
                partner=self.partner) as work:
            self.service = work.component(usage='sale')

    def test_read_sale(self):
        self.sale.action_confirm()
        res = self.service.get(self.sale.id)
        self.assertEqual(res['id'], self.sale.id)
        self.assertEqual(res['name'], self.sale.name)

    def test_allow_read_cart(self):
        res = self.service.get(self.sale.id)
        self.assertEqual(res['id'], self.sale.id)
        self.assertEqual(res['name'], self.sale.name)

    # def test_list_sale(self):
        # TODO we should filter the cart

    def test_hack_read_other_customer_sale(self):
        sale = self.env.ref('sale.sale_order_1')
        sale.shopinvader_backend_id = self.backend
        # We raise a not found error because in a point of view of the hacker
        # and his right the record does not exist
        with self.assertRaises(NotFound):
            self.service.get(sale.id)
