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
        """create should not create a new job."""
        job = self.job_counter()
        self._create_incoming_move()
        self.assertEqual(job.count_created(), 0)

    def test_action_cancel(self):
        """action_cancel should create a new job."""
        job = self.job_counter()
        move = self._create_incoming_move()
        move._action_cancel()
        self.assertEqual(job.count_created(), 1)

    def test_action_confirm(self):
        """action_confirm should create a new job."""
        job = self.job_counter()
        move = self._create_incoming_move()
        move._action_confirm()
        self.assertEqual(job.count_created(), 1)

    def test_action_done(self):
        """action_done should create a new job."""
        job = self.job_counter()
        move = self._create_incoming_move()
        move._action_done()
        self.assertEqual(job.count_created(), 1)

    def test_action_confirm_not_bound(self):
        """action_confirm for non bound products should not create a job."""
        job = self.job_counter()
        self.product.shopinvader_bind_ids.unlink()
        move = self._create_incoming_move()
        move._action_confirm()
        self.assertEqual(job.count_created(), 0)

    def test_duplicated_action_done(self):
        """action_done should create a new job."""
        job = self.job_counter()
        move = self._create_incoming_move()
        move._action_done()
        move = self._create_incoming_move()
        move._action_done()
        self.assertEqual(job.count_created(), 1)
