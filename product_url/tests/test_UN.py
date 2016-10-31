# -*- coding: utf-8 -*-
import unittest
from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError



class Test_un(unittest.TestCase):

    def test_somme(self):
        a=2
        b=3
        c= a+b
        print "Test somme "+str(c)
        self.assertEquals(c,5)

    def test_upper(self):
        # import pdb; pdb.set_trace()
        self.assertEqual('foo'.upper(), 'FOO')







