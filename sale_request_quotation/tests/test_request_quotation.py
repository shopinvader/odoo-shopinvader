# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase
import logging
_logger = logging.getLogger(__name__)



class Testrequest_quotation(SingleTransactionCase):

    
    def setup(self):
        super(Testrequest_quotation, self).setup()

    def test_init1(self):
        sale = self.env['sale.order'].browse(7)

        self.assertEqual('request_quotation', sale.sub_state)

    def test_init2(self):
        sale = self.env['sale.order'].browse(8)

        self.assertEqual('request_quotation', sale.sub_state)

    def test_init4(self):
        sale = self.env['sale.order'].browse(2)

        self.assertFalse('request_quotation' == sale.sub_state)


