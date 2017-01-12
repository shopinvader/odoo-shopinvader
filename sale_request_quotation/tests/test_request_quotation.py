# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase
import logging
_logger = logging.getLogger(__name__)


class TestRequestQuotation(SingleTransactionCase):

    def setup(self):
        super(TestRequestQuotation, self).setup()

    def test_init1(self):
        sale = self.env.ref('sale.sale_order_7')

        self.assertEqual('request_quotation', sale.sub_state)

    def test_init2(self):
        sale = self.env.ref('sale.sale_order_8')

        self.assertEqual('request_quotation', sale.sub_state)

    def test_init4(self):
        sale = self.env.ref('sale.sale_order_2')

        self.assertFalse('request_quotation' == sale.sub_state)
