# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import (
    CartCase,
    CommonConnectedCartCase,
)


class ShopinvaderCartQuotationCase(CommonConnectedCartCase):
    def test_request_quotation(self):
        self.assertEqual(self.cart.typology, "cart")
        self.service.dispatch("request_quotation", params={})
        self.assertEqual(self.cart.typology, "quotation")

    def test_only_quotation_in_cart_info(self):
        response = self.service.dispatch("search")
        self.assertIn(
            "only_quotation", response["data"]["lines"]["items"][0]["product"]
        )


class CommonConnectedQuotationCase(CartCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.cart = self.env.ref("shopinvader.sale_order_2")
        self.shopinvader_session = {"cart_id": self.cart.id}
        self.partner = self.env.ref("shopinvader.partner_1")
        self.address = self.env.ref("shopinvader.partner_1_address_1")
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")
        self.service.dispatch("request_quotation", params={})
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="quotations")
