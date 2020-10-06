# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestMultiUserCommon


class TestMultiUserPartner(TestMultiUserCommon):
    """Test partner methods and fields.
    """

    def test_get_customer_partner_default(self):
        customer_partner = self.company.get_customer_partner(self.backend)
        self.assertEqual(customer_partner, self.company)
        self.assertEqual(
            self.company_binding.main_partner_id, self.company_binding
        )

    def test_get_customer_partner_multi_enabled_default(self):
        self.backend.customer_multi_user = True
        self.assertEqual(
            self.backend.multi_user_profile_policy, "main_partner"
        )

        customer_partner = self.company.get_customer_partner(self.backend)
        self.assertEqual(customer_partner, self.company)

        # as we have only the company account, nothing changes when user_partner is on
        self.backend.multi_user_profile_policy = "user_partner"
        customer_partner = self.company.get_customer_partner(self.backend)
        self.assertEqual(customer_partner, self.company)

    def test_get_customer_partner_multi_enabled_simple_user(self):
        self.backend.customer_multi_user = True
        self.backend.multi_user_profile_policy = "user_partner"
        # check info on binding
        self.assertTrue(self.invader_user.is_invader_user)
        self.assertEqual(
            self.invader_user.main_partner_id, self.company_binding
        )
        # check info on partner
        partner = self.invader_user.record_id
        self.assertTrue(partner.is_invader_user)

        # check info on company
        customer_partner = self.company.get_customer_partner(self.backend)
        self.assertEqual(customer_partner, self.company)

        # now we get the same partner as customer
        customer_partner = partner.get_customer_partner(self.backend)
        self.assertEqual(customer_partner, partner)
