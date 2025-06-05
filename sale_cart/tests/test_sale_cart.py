# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import SaleCartCommon


class TestSaleCart(SaleCartCommon):
    def test_action_confirm_cart(self):
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("cart", self.so_cart.typology)
        self.so_cart.action_confirm_cart()
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("sale", self.so_cart.typology)

    def test_action_confirm(self):
        self.assertEqual("draft", self.so_cart.state)
        self.assertEqual("cart", self.so_cart.typology)
        self.so_cart.action_confirm()
        self.assertEqual("sale", self.so_cart.state)
        self.assertEqual("sale", self.so_cart.typology)
