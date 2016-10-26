# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError

class TestBaseUrl(TransactionCase):

    # def setup(self):
    #     super (TestBaseUrl,self).setup()
    #     print self.registry
    #     self.url_reg = self.registry('url.url')

    def test_false(self):
        
        self.assertFalse(False)