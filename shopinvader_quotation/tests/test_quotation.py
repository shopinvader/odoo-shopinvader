# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2021 Camptocamp (http://www.camptocamp.com)
# @author Simone Orsi <simone.orsi@camptocamp.com>
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

    def test_send(self):
        order = self.cart.copy({"typology": "sale"})
        self.assertEqual(order.typology, "sale")
        order.action_quotation_sent()
        self.assertEqual(order.state, "sent")
        self.assertEqual(order.typology, "quotation")

    def test_visibility(self):
        order = self.cart.copy({"typology": "sale"})
        response = self.quotation_service.dispatch("search")
        self.assertNotIn(order.id, [x["id"] for x in response["data"]])
        self.backend.quotation_expose_all = True
        response = self.quotation_service.dispatch("search")
        self.assertNotIn(order.id, [x["id"] for x in response["data"]])
        order.action_quotation_sent()
        response = self.quotation_service.dispatch("search")
        self.assertIn(order.id, [x["id"] for x in response["data"]])

    def test_visibility_multi_backends(self):
        backend2 = self.env.ref("shopinvader.backend_2")
        self.backend.quotation_expose_all = True
        backend2.quotation_expose_all = True
        order = self.cart.copy({"typology": "quotation"})
        order2 = self.cart.copy(
            {"typology": "quotation", "shopinvader_backend_id": backend2.id}
        )
        order_not_bound = self.cart.copy(
            {"typology": "quotation", "shopinvader_backend_id": False}
        )

        response = self.quotation_service.dispatch("search")
        self.assertIn(order.id, [x["id"] for x in response["data"]])
        self.assertIn(order_not_bound.id, [x["id"] for x in response["data"]])
        self.assertNotIn(order2.id, [x["id"] for x in response["data"]])

        # Switch backend
        self.quotation_service.work.shopinvader_backend = backend2
        response = self.quotation_service.dispatch("search")
        self.assertIn(order2.id, [x["id"] for x in response["data"]])
        self.assertIn(order_not_bound.id, [x["id"] for x in response["data"]])
        self.assertNotIn(order.id, [x["id"] for x in response["data"]])

    def test_confirm_from_shop(self):
        order = self.cart.copy(
            {"typology": "quotation", "shopinvader_backend_id": False}
        )
        self.assertEqual(order.typology, "quotation")
        self.assertFalse(order.shopinvader_backend_id)
        self.quotation_service.dispatch("confirm", order.id)
        self.assertEqual(order.typology, "sale")
        self.assertEqual(order.shopinvader_backend_id, self.backend)
