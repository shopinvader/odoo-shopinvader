# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductNew(TransactionCase):

    def setUp(self):
        super(TestProductNew, self).setUp()

    def test_scheduler_new_product(self):
        self.env['product.template'].compute_new_product(1, extra_domain=[])
        products = self.env['product.template'].search(
            [('shopinvader_bind_ids', '!=', False)],
            limit=1, order='create_date desc')
        for product in products:
            self.assertEqual(product.new_product, True)
        new_products = self.env['product.template'].search(
            [('new_product', '=', True)])
        self.assertEqual(len(new_products), 1)
