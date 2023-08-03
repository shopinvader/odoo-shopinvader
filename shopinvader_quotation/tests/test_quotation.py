# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_v1_base.tests.test_cart import CommonConnectedCartCase


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

    def test_send(self):
        order = self.cart.copy({"typology": "sale"})
        self.assertEqual(order.typology, "sale")
        order.action_quotation_sent()
        self.assertEqual(order.state, "sent")
        self.assertEqual(order.typology, "quotation")

    def test_send_message_post(self):
        order = self.cart.copy({"typology": "sale"})
        self.assertEqual(order.typology, "sale")
        action = order.action_quotation_send()
        # pylint: disable=translation-required
        order.with_context(action["context"]).message_post(body="Test")
        self.assertEqual(order.state, "sent")
        self.assertEqual(order.typology, "quotation")

    def test_visibility(self):
        order = self.cart.copy({"typology": "sale"})
        response = self.quotation_service.dispatch("search")
        self.assertNotIn(order.id, [x["id"] for x in response["data"]])
        order.action_quotation_sent()
        response = self.quotation_service.dispatch("search")
        self.assertIn(order.id, [x["id"] for x in response["data"]])

    def test_search_pagination(self):
        quotation = self.cart.copy({"typology": "quotation"})
        quotation.copy()
        quotation.copy()
        params = {"per_page": 2}
        res = self.quotation_service.dispatch("search", params=params)["data"]
        self.assertEqual(len(res), 2)
        params = {"per_page": 2, "page": 2}
        res = self.quotation_service.dispatch("search", params=params)["data"]
        self.assertEqual(len(res), 1)
