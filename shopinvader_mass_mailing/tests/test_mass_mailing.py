# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import CommonMassMailingCase


class TestMassMailing(CommonMassMailingCase):
    def test_get(self):
        res = self.service.dispatch("get", self.mailing_list.id)
        self.assertEqual(res["id"], self.mailing_list.id)
        self.assertEqual(res["name"], self.mailing_list.name)

    def test_search(self):
        res = self.service.dispatch("search", params={})
        all_lists = self.env["mailing.list"].search([("is_public", "=", True)])
        self.assertEqual(res["size"], len(all_lists))
        for data, mailing_list in zip(res["data"], all_lists):
            self.assertEqual(data["name"], mailing_list.name)

    def test_subscribe(self):
        res = self.service.dispatch(
            "subscribe",
            self.mailing_list.id,
            params={"email": "subscriber@example.com"},
        )
        self.assertEqual(res["success"], True)
        subs = self._get_subscription(self.mailing_list, "subscriber@example.com")
        self.assertTrue(subs)
        self.assertFalse(subs.opt_out)

    def test_unsubscribe(self):
        # Case 1: Email is not subscribed
        res = self.service.dispatch(
            "unsubscribe",
            self.mailing_list.id,
            params={"email": "subscriber@example.com"},
        )
        self.assertFalse(res["success"])
        self.assertEqual(res["message"], "Not subscribed")
        subs = self._get_subscription(self.mailing_list, "subscriber@example.com")
        self.assertFalse(subs)
        # Case 2: Email is subscribed
        res = self.service.dispatch(
            "unsubscribe",
            self.mailing_list.id,
            params={"email": self.mailing_contact.email},
        )
        self.assertTrue(res["success"])
        subs = self._get_subscription(self.mailing_list, self.mailing_contact.email)
        self.assertTrue(subs.opt_out)

    def test_unsubscribe_all(self):
        # Create a second mailing list and subscribe mailing_contact to it
        another_list = self.mailing_list.copy({"name": "Another List"})
        self.mailing_contact.list_ids = [(4, another_list.id)]
        # Unsubscribe from all lists
        res = self.service.dispatch(
            "unsubscribe_all",
            params={"email": self.mailing_contact.email},
        )
        self.assertTrue(res["success"])
        for mailing_list in self.mailing_list | another_list:
            subs = self._get_subscription(mailing_list, self.mailing_contact.email)
            self.assertTrue(subs.opt_out)
