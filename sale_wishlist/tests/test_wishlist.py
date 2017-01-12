# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase
import logging
_logger = logging.getLogger(__name__)


class Testwishlist(SingleTransactionCase):

    def setup(self):
        super(Testwishlist, self).setup()

    def test_init3(self):
        sale = self.env.ref('sale.sale_order_3')

        self.assertEqual('wishlist', sale.sub_state)

    def test_init5(self):
        sale = self.env.ref('sale.sale_order_5')

        self.assertEqual('wishlist', sale.sub_state)

    def test_init6(self):
        sale = self.env.ref('sale.sale_order_6')

        self.assertEqual('wishlist', sale.sub_state)
