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
        self._init_job_counter()
        self._create_incomming_move()
        self._check_nbr_job_created(0)

    def test_action_cancel(self):
        """
        Test the function action_cancel() on stock.move who should create a
        new queue.job
        :return:
        """
        self._init_job_counter()
        move = self._create_incomming_move()
        move._action_cancel()
        self._check_nbr_job_created(1)

    def test_action_confirm(self):
        """
        Test the function action_confirm() on stock.move who should create a
        new queue.job
        :return:
        """
        self._init_job_counter()
        move = self._create_incomming_move()
        move._action_confirm()
        self._check_nbr_job_created(1)

    def test_action_done(self):
        """
        Test the function action_done() on stock.move who should create a
        new queue.job
        :return:
        """
        self._init_job_counter()
        move = self._create_incomming_move()
        move._action_done()
        self._check_nbr_job_created(1)

    def test_action_confirm_not_binded(self):
        """
        Test the function action_confirm() on stock.move with a not binded
        product should not create a new queue.job
        :return:
        """
        self._init_job_counter()
        self.product.shopinvader_bind_ids.unlink()
        move = self._create_incomming_move()
        move._action_confirm()
        self._check_nbr_job_created(0)

    def test_duplicated_action_done(self):
        """
        Test the function action_done() on stock.move who should create a
        new queue.job
        :return:
        """
        self._init_job_counter()
        move = self._create_incomming_move()
        move._action_done()
        move = self._create_incomming_move()
        move._action_done()
        self._check_nbr_job_created(1)
