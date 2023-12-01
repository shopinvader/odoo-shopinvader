# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.shopinvader_sale_state.tests.common import CommonSaleState


class TestSaleState(CommonSaleState):
    def test_state_partial(self):
        self.sale.action_confirm()
        # We force the state for the test
        # as we do not depend on sale_stock_delivery_state and stock can
        # be installed in the database
        self.sale.delivery_status = "partial"
        self.assertEqual(self.sale.shopinvader_state, "delivery_partial")

    def test_state_full(self):
        self.sale.action_confirm()
        self.sale.delivery_status = "full"
        self.assertEqual(self.sale.shopinvader_state, "delivery_full")
