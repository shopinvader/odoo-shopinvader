# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import CommonSaleState


class TestSaleState(CommonSaleState):
    def test_state_pending(self):
        self.assertEqual(self.sale.shopinvader_state, "pending")

    def test_state_pending_sent(self):
        self.sale.action_quotation_sent()
        self.assertEqual(self.sale.shopinvader_state, "pending")

    def test_state_processing(self):
        self.sale.action_confirm()
        self.assertEqual(self.sale.shopinvader_state, "processing")

    def test_state_delivery_full(self):
        self.sale.action_confirm()
        self.sale.action_done()
        self.assertEqual(self.sale.shopinvader_state, "delivery_full")
