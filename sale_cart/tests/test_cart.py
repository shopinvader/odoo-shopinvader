# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase
import logging
_logger = logging.getLogger(__name__)


class Testcart(SingleTransactionCase):

    def setup(self):
        super(Testcart, self).setup()

    def test_init1(self):
        sale = self.env['sale.order'].browse(1)

        self.assertEqual('cart', sale.sub_state)

    def test_init2(self):
        sale = self.env['sale.order'].browse(2)

        self.assertEqual('cart', sale.sub_state)

    def test_init4(self):
        sale = self.env['sale.order'].browse(4)

        self.assertEqual('cart', sale.sub_state)
