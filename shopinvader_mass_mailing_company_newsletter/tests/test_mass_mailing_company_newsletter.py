# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_address import CommonAddressCase


class TestAddress(CommonAddressCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.address_params["email"] = "purple@example.com"

    def test_create(self):
        params = self.address_params.copy()
        params["email"] = "purple@example.com"
        params["newsletter_subscription"] = "subscribed"
        existing = [address["id"] for address in self.address_service.search()["data"]]
        data = self.address_service.dispatch("create", params=params)["data"]
        partner_id = [d["id"] for d in data if d["id"] not in existing][0]
        partner = self.env["res.partner"].browse(partner_id)
        self.assertEqual(partner.main_mailing_list_subscription_state, "subscribed")

    def test_update(self):
        # Subscribe
        params = {"newsletter_subscription": "subscribed"}
        self.address_service.dispatch("update", self.partner.id, params=params)
        self.assertEqual(
            self.partner.main_mailing_list_subscription_state, "subscribed"
        )
        # Unsubscribe
        params = {"newsletter_subscription": "unsubscribed"}
        self.address_service.dispatch("update", self.partner.id, params=params)
        self.assertEqual(
            self.partner.main_mailing_list_subscription_state, "unsubscribed"
        )
