# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestRequestQuotation(TransactionCase):

    def test_order_is_request_quotation(self):
        sale = self.env.ref('sale.sale_order_3')
        self.assertEqual('request_quotation', sale.sub_state)
