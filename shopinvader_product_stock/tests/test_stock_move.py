# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import StockCommonCase


class TestStockMove(StockCommonCase):
    """
    Tests for stock.move
    """

    def test_create_move(self):
        """
        Test the function create on stock.move who should not create a
        new queue.job
        :return:
        """
        job = self.job_counter()
        self._create_incomming_move()
        self.assertEqual(job.count_created(), 0)

    def test_action_cancel(self):
        """
        Test the function action_cancel() on stock.move who should create a
        new queue.job
        :return:
        """
        job = self.job_counter()
        move = self._create_incomming_move()
        move.action_cancel()
        self.assertEqual(job.count_created(), 1)

    def test_action_confirm(self):
        """
        Test the function action_confirm() on stock.move who should create a
        new queue.job
        :return:
        """
        job = self.job_counter()
        move = self._create_incomming_move()
        move.action_confirm()
        self.assertEqual(job.count_created(), 1)

    def test_action_done(self):
        """
        Test the function action_done() on stock.move who should create a
        new queue.job
        :return:
        """
        job = self.job_counter()
        move = self._create_incomming_move()
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
        move = self._create_incomming_move()
        move.action_confirm()
        self.assertEqual(job.count_created(), 0)

    def test_duplicated_action_done(self):
        """
        Test the function action_done() on stock.move who should create a
        new queue.job
        :return:
        """
        job = self.job_counter()
        move = self._create_incomming_move()
        move.action_done()
        move = self._create_incomming_move()
        move.action_done()
        self.assertEqual(job.count_created(), 1)
