# -*- coding: utf-8 -*-
import unittest


class TestUN(unittest.TestCase):

    def test_somme(self):
        a = 2
        b = 3
        c = a+b
        print "Test somme "+str(c)
        self.assertEquals(c, 5)

    def test_upper(self):
        # import pdb; pdb.set_trace()
        self.assertEqual('foo'.upper(), 'FOO')
