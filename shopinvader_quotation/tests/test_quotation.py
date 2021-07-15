# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class ShopinvaderCartQuotationCase(CommonConnectedCartCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.quotation_service = work.component(usage="quotations")

    def test_quotation(self):
        self.assertEqual(self.cart.typology, "cart")
        self.service.dispatch("request_quotation", params={})
        self.assertEqual(self.cart.typology, "quotation")
        # Confirm it to sale
        self.quotation_service.dispatch("confirm", self.cart.id)
        self.assertEqual(self.cart.typology, "sale")

    def test_only_quotation_in_cart_info(self):
        response = self.service.dispatch("search")
        self.assertIn(
            "only_quotation", response["data"]["lines"]["items"][0]["product"]
        )
