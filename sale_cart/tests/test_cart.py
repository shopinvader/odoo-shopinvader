# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase
import logging
_logger = logging.getLogger(__name__)


class Testcart(SingleTransactionCase):

    def setup(self):
        super(Testcart, self).setup()

    def test_init1(self):
        sale = self.env.ref('sale.sale_order_1')

        self.assertEqual('cart', sale.sub_state)

    def test_init2(self):
        sale = self.env.ref('sale.sale_order_2')

        self.assertEqual('cart', sale.sub_state)

    def test_init4(self):
        sale = self.env.ref('sale.sale_order_4')

        self.assertEqual('cart', sale.sub_state)
