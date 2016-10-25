# -*- coding: utf-8 -*-
import unittest
from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError



class TestalaCon(unittest.TestCase):
    def setUp(self):
        self.test_somme()
        self.test_upper()

    def test_somme(self):
        a=2
        b=3
        c= a+b
        print "COUCOUCOCUOCUCOUCOCU "+str(c)
        self.assertEquals(c,6)

    def test_upper(self):
        # import pdb; pdb.set_trace()
        self.assertEqual('foo'.upper(), 'FOO')


    print  "DANS TEST A LA CON"
class TestConnector(unittest.TestCase):
        def create_attachment(self):
            print "zzzzzzzzzzzzzzzzzooooooooooooooooooooobbbbbbbbbbbbbb"



# class Test_Test(TransactionCase):
#     """Test dumy functions."""
#
#     print "cocococococococo"
#
#     def test_isupper(self):
#         self.assertTrue('FOO'.isupper())
#         print "TESTTEST"
#         self.assertFalse('Foo'.isupper())
#
#     def test_test(self):
#         self.assertTrue(False)
#
#     def test_split(self):
#         s = 'hello world'
#         self.assertEqual(s.split(), ['hello', 'world'])
#         # check that s.split fails when the separator is not a string
#         with self.assertRaises(TypeError):
#             s.split(2)
#
#     def base_testUn(self):
#         product = self.env['product.product'].search([('id','=',51)])
#         print (product.name)
#         print (product.name)
#         print (product.name)
#         print (product.name)
#         print (product.name)
#         print (product.name)
#         print (product.name)
#         print (product.name)
#         print (product.name)
#         print (product.name)
#         print (product.name)

#class TestStringMethods(unittest.TestCase):








