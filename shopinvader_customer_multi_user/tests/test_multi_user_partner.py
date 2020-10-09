# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestMultiUserCommon


class TestMultiUserPartner(TestMultiUserCommon):
    """Test partner methods and fields.
    """

    def test_get_customer_partner_default(self):
        self.assertEqual(
            self.company.get_customer_partner(self.backend), self.company
        )
        self.assertEqual(
            self.user_binding.record_id.get_customer_partner(self.backend),
            self.user_binding.record_id,
        )

    def test_main_partner_default(self):
        self.assertEqual(
            # this is already the main partner, get nothing
            self.company_binding.main_partner_id,
            self.company.browse(),
        )
        self.assertEqual(self.user_binding.main_partner_id, self.company)

    def test_invader_parent(self):
        self.assertEqual(
            self.company_binding.invader_parent_id,
            self.company_binding.browse(),
        )
        self.assertEqual(
            self.user_binding.invader_parent_id, self.company_binding
        )

    def test_is_invader_user(self):
        self.assertFalse(self.company_binding.is_invader_user)
        self.assertFalse(self.company.has_invader_user)
        self.assertTrue(self.user_binding.is_invader_user)
        self.assertTrue(self.user_binding.record_id.has_invader_user)

    def test_get_customer_partner_multi_enabled_company(self):
        self.backend.customer_multi_user = True
        self.assertEqual(
            self.backend.multi_user_profile_policy, "main_partner_id"
        )
        customer_partner = self.company.get_customer_partner(self.backend)
        self.assertEqual(customer_partner, self.company)

        # as we have only the company account, nothing changes when user_partner is on
        self.backend.multi_user_profile_policy = "record_id"
        customer_partner = self.company.get_customer_partner(self.backend)
        self.assertEqual(customer_partner, self.company)

    def test_get_customer_partner_multi_enabled_simple_user(self):
        self.backend.customer_multi_user = True
        self.assertEqual(
            self.backend.multi_user_profile_policy, "main_partner_id"
        )

        customer_partner = self.user_binding.record_id.get_customer_partner(
            self.backend
        )
        self.assertEqual(customer_partner, self.user_binding.main_partner_id)

        # change policy
        self.backend.multi_user_profile_policy = "record_id"
        # now we get the same partner as customer
        customer_partner = self.user_binding.record_id.get_customer_partner(
            self.backend
        )
        self.assertEqual(customer_partner, self.user_binding.record_id)
