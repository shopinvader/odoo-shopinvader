# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from random import randint
from contextlib import contextmanager
from odoo import api, models
from odoo.addons.component.tests.common import SavepointComponentCase
from odoo.addons.queue_job.tests.common import JobMixin


class TestStockMove(SavepointComponentCase, JobMixin):
    """
    Tests for stock.move
    """

    def setUp(self):
        super(TestStockMove, self).setUp()
        self.env = api.Environment(self.cr, self.uid, {})
        self.shopinvader_backend = self.env.ref('shopinvader.backend_1')
        self.shopinvader_backend.product_stock_field_id = self.env.ref(
            "stock.field_product_product_qty_available")
        self.shopinvader_backend.bind_all_product()
        self.loc_supplier = self.env.ref('stock.stock_location_suppliers')
        self.product = self.env.ref('product.product_product_8')
        self.picking_type_in = self.env.ref("stock.picking_type_in")

    def _create_move(self):
        return self.env['stock.move'].create({
            'name': 'Forced Move',
            'location_id': self.loc_supplier.id,
            'location_dest_id': self.picking_type_in.default_location_dest_id.id,
            'product_id': self.product.id,
            'product_uom_qty': 2.0,
            'product_uom': self.product.uom_id.id,
            'picking_type_id': self.picking_type_in.id,
        })

    def test_create_move(self):
        """
        Test the function create on stock.move who should not create a
        new queue.job
        :return:
        """
        job = self.job_counter()
        move = self._create_move()
        self.assertEqual(job.count_created(), 0)

    def test_action_cancel(self):
        """
        Test the function action_cancel() on stock.move who should create a
        new queue.job
        :return:
        """
        job = self.job_counter()
        move = self._create_move()
        move.action_cancel()
        self.assertEqual(job.count_created(), 1)

    def test_action_confirm(self):
        """
        Test the function action_confirm() on stock.move who should create a
        new queue.job
        :return:
        """
        job = self.job_counter()
        move = self._create_move()
        move.action_confirm()
        self.assertEqual(job.count_created(), 1)

    def test_action_done(self):
        """
        Test the function action_done() on stock.move who should create a
        new queue.job
        :return:
        """
        job = self.job_counter()
        move = self._create_move()
        move.action_done()
        self.assertEqual(job.count_created(), 1)

    def test_action_confirm_not_binded(self):
        """
        Test the function action_confirm() on stock.move with a not binded
        product should not create a new queue.job
        :return:
        """
        job = self.job_counter()
        self.product.shopinvader_bind_ids.unlink()
        move = self._create_move()
        move.action_confirm()
        self.assertEqual(job.count_created(), 0)
