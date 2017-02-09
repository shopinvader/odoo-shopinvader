# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class Testcart(TransactionCase):

    def test_order_is_cart(self):
        sale = self.env.ref('sale.sale_order_2')
        self.assertEqual('cart', sale.sub_state)
