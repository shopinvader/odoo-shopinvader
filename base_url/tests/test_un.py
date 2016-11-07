# -*- coding: utf-8 -*-
#    Copyright (C) 2013 Akretion (http://www.akretion.com)
#    @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import SingleTransactionCase
import logging
_logger = logging.getLogger(__name__)


class Testun(SingleTransactionCase):

    def test_somme(self):
        a = 2
        b = 3
        c = a+b
        _logger.info("Test somme " + str(c))
        self.assertEquals(c, 5)

    def test_upper(self):
        # import pdb; pdb.set_trace()
        self.assertEqual('foo'.upper(), 'FOO')
