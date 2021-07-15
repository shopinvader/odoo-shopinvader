# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestMultiUserCommon


class TestMultiUserCustomer(TestMultiUserCommon):
    """Test interaction with /customer endpoint."""

    def test_create_customer_no_multi_user(self):
        self.backend.customer_multi_user = False
        self.data.update({"external_id": "cust1"})
        params = dict(self.data, company_token="ABCDEF")
        res = self.service.dispatch("create", params=params)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        self.assertFalse(partner.parent_id)
        self.assertFalse(partner.has_invader_user)
        self._test_partner_data(partner, self.data)

    def test_create_customer_multi_user(self):
        self.backend.customer_multi_user = True
        data = dict(self.data, external_id="new1", email="new@one.com", name="New One")
        # customer 1
        params = dict(data, company_token="ABCDEF")
        res = self.service.dispatch("create", params=params)["data"]
        partner1 = self.env["res.partner"].browse(res["id"])
        self.assertEqual(partner1.parent_id, self.company)
        self.assertEqual(partner1.type, "contact")
        self.assertTrue(partner1.has_invader_user)
        self._test_partner_data(partner1, data)
        # customer 2
        data = dict(self.data, external_id="new2", email="new@two.com", name="New Two")
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

    def test_update_customer_multi_user_store_cache(self):
        self.backend.customer_multi_user = True
        data = dict(self.data, external_id="new1", email="new@one.com", name="New One")
        # customer 1
        params = dict(data, company_token="ABCDEF")
        res = self.service.dispatch("create", params=params)["data"]
        partner1 = self.env["res.partner"].browse(res["id"])
        # Update happens via address service. To be changed as per
        # https://github.com/shopinvader/odoo-shopinvader/issues/530
        params["name"] = params["name"] + " UPDATED!"
        self._update_work_ctx(self.address_service, partner=partner1)
        res = self.address_service.dispatch("update", partner1.id, params=params)
        # By default the customer partner is the main partner
        # hence we are not editing the main profile and we don't need cache
        self.assertNotIn("store_cache", res)
        # Change the policy
        self.backend.multi_user_profile_policy = "record_id"
        params["name"] = params["name"] + " UPDATED 2 times!"
        res = self.address_service.dispatch("update", partner1.id, params=params)
        self.assertTrue(
            res["store_cache"]["customer"]["name"].endswith(" UPDATED 2 times!")
        )

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

    def test_company_data_multi_user_off(self):
        self.backend.customer_multi_user = False
        service = self._get_service(partner=self.company, usage="customer")
        res = service._to_customer_info(self.company)
        # multi user not enabled
        self.assertNotIn("company_token", res)
        self.assertNotIn("main_account", res)
        self.assertNotIn("is_simple_user", res)

    def test_company_data_multi_user_on(self):
        # check on the company
        service = self._get_service(partner=self.company, usage="customer")
        res = service._to_customer_info(self.company)
        self.assertEqual(res["company_token"], "ABCDEF")
        self.assertFalse(res["is_simple_user"])
        # same user of the company
        self.assertEqual(res["main_account"], None)

    def test_simple_user_data_multi_user_on(self):
        # check on a simple user
        service = self._get_service(
            partner=self.user_binding.record_id, usage="customer"
        )
        res = service._to_customer_info(self.user_binding.record_id)
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
