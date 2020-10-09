# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestMultiUserCommon


class TestMultiUserCustomer(TestMultiUserCommon):
    """Test interaction with /customer endpoint.
    """

    def test_create_customer_no_multi_user(self):
        self.data.update({"external_id": "cust1"})
        params = dict(self.data, company_token="ABCDEF")
        res = self.service.dispatch("create", params=params)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        self.assertFalse(partner.parent_id)
        self.assertFalse(partner.has_invader_user)
        self._test_partner_data(partner, self.data)

    def test_create_customer_multi_user(self):
        self.backend.customer_multi_user = True
        data = dict(
            self.data, external_id="new1", email="new@one.com", name="New One"
        )
        # customer 1
        params = dict(data, company_token="ABCDEF")
        res = self.service.dispatch("create", params=params)["data"]
        partner1 = self.env["res.partner"].browse(res["id"])
        self.assertEqual(partner1.parent_id, self.company)
        self.assertEqual(partner1.type, "contact")
        self.assertTrue(partner1.has_invader_user)
        self._test_partner_data(partner1, data)
        # customer 2
        data = dict(
            self.data, external_id="new2", email="new@two.com", name="New Two"
        )
        params = dict(data, company_token="ABCDEF")
        res = self.service.dispatch("create", params=params)["data"]
        partner2 = self.env["res.partner"].browse(res["id"])
        self.assertEqual(partner2.parent_id, self.company)
        self.assertEqual(partner2.type, "contact")
        self.assertTrue(partner2.has_invader_user)
        self._test_partner_data(partner2, data)
        # both are there
        self.assertIn(partner1, self.company.child_ids)
        self.assertIn(partner2, self.company.child_ids)
        # the company is not an invader user
        self.assertFalse(self.company.has_invader_user)

    def test_create_customer_multi_user_wrong_token(self):
        self.data.update({"external_id": "cust1"})
        params = dict(self.data, company_token="WRONG_TOKEN")
        res = self.service.dispatch("create", params=params)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        # partner is created normally, no relation w/ the company
        self.assertFalse(partner.parent_id)
        self.assertFalse(partner.has_invader_user)
        self._test_partner_data(partner, self.data)
        self.assertNotIn(partner, self.company.child_ids)
        self.assertFalse(self.company.has_invader_user)

    def test_customer_data(self):
        res = self.service._to_customer_info(self.company)
        # multi user not enabled
        self.assertNotIn("company_token", res)
        self.assertNotIn("main_account", res)
        self.assertNotIn("is_simple_user", res)

        # enable it
        self.backend.customer_multi_user = True

        # check on the company
        res = self.service._to_customer_info(self.company)
        self.assertEqual(res["company_token"], "ABCDEF")
        self.assertFalse(res["is_simple_user"])
        # same user of the company
        self.assertEqual(res["main_account"], None)

        # check on a simple user
        res = self.service._to_customer_info(self.invader_user.record_id)
        self.assertTrue(res["is_simple_user"])
        self.assertNotIn("company_token", res)
        self.assertEqual(
            res["main_account"],
            {
                "id": self.company.id,
                "name": self.company.name,
                "ref": self.company.ref,
            },
        )
