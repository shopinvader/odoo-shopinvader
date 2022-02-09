# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestMultiUserPartnerDomainCommon


class TestMultiUserServicePartnerDomain(TestMultiUserPartnerDomainCommon):
    """Test partner domains for services"""

    # Company can see always everything
    def test_user_company__record_id(self):
        self._test_partner_records(
            self.company,
            addresses=self.all_partners + self.all_addresses,
            orders=self.all_orders,
            invoices=self.all_invoices,
        )

    def test_user_company__parent_id(self):
        self.backend.multi_user_records_policy = "parent_id"
        self._test_partner_records(
            self.company,
            addresses=self.all_partners + self.all_addresses,
            orders=self.all_orders,
            invoices=self.all_invoices,
        )

    def test_user_company__main_partner_id(self):
        self.backend.multi_user_records_policy = "main_partner_id"
        self._test_partner_records(
            self.company,
            addresses=self.all_partners + self.all_addresses,
            orders=self.all_orders,
            invoices=self.all_invoices,
        )

    def test_user_direct_child_of_company__record_id(self):
        """Direct child sees only its own records."""
        # For this test, consider all addresses as private
        self.all_public_addresses.write({"invader_address_share_policy": "private"})
        self._test_user_direct_child_of_company__record_id(self.user)
        self._test_user_direct_child_of_company__record_id(self.user2)
        self._test_user_direct_child_of_company__record_id(self.user3)

    def test_user_direct_child_of_company__parent_id(self):
        """Direct child sees only its own records and the ones from direct parent."""
        self.backend.multi_user_records_policy = "parent_id"
        # Case 1: User 1 sees only its own records, the ones from its direct parent,
        # and the publicly shared ones from their sibilings
        partner = self.user
        expected_addresses = (
            partner
            | self.company
            | self._get_addresses(self.company, policy="public")
            | self._get_addresses(self.user, policy="private")
            | self.all_public_addresses
        )
        self._test_user_direct_child_of_company__parent_id(
            partner, self.company, expected_addresses=expected_addresses
        )
        # Case 2: User 2 sees only its own records, the ones from its direct parent,
        # and the publicly shared ones from their sibilings
        partner = self.user2
        expected_addresses = (
            partner
            | self.company
            | self._get_addresses(self.company, policy="public")
            | self._get_addresses(self.user2, policy="private")
            | self.all_public_addresses
        )
        self._test_user_direct_child_of_company__parent_id(
            partner, self.company, expected_addresses=expected_addresses
        )
        # Case 3: User 3 sees only its own records, the ones from its direct parent,
        # and the publicly shared ones from their sibilings
        partner = self.user3
        expected_addresses = (
            partner
            | self.user2
            | self._get_addresses(self.user3)
            | self._get_addresses(self.user2, policy="public")
        )
        self._test_user_direct_child_of_company__parent_id(
            partner,
            self.user2,
            expected_addresses=expected_addresses,
        )
        # Case 4: main partner is the parent in this case
        # but if we set the company, then they can see records from the company as well
        self.user3_binding.main_partner_id = self.company
        expected_addresses |= (
            self.company
            | self._get_addresses(self.company, policy="public")
            | self.all_public_addresses
        )
        self._test_user_direct_child_of_company__parent_id(
            partner,
            self.company + self.user2,
            expected_addresses=expected_addresses,
        )

    def test_user_direct_child_of_company__main_partner_id(self):
        """Direct child sees only its own records and the ones from main partner."""
        self.backend.multi_user_records_policy = "main_partner_id"
        # Case 1: User 1 sees only its own records, the ones from its main partner,
        # and the publicly shared ones from their sibilings
        partner = self.user
        expected_addresses = (
            partner
            | self.company
            | self._get_addresses(self.company, policy="public")
            | self._get_addresses(self.user, policy="private")
            | self.all_public_addresses
        )
        self._test_user_direct_child_of_company__parent_id(
            partner, self.company, expected_addresses=expected_addresses
        )
        # Case 2: User 2 sees only its own records, the ones from its main partner,
        # and the publicly shared ones from their sibilings
        partner = self.user2
        expected_addresses = (
            partner
            | self.company
            | self._get_addresses(self.company, policy="public")
            | self._get_addresses(self.user2, policy="private")
            | self.all_public_addresses
        )
        self._test_user_direct_child_of_company__parent_id(
            partner, self.company, expected_addresses=expected_addresses
        )
        # Case 3: Change User 2's main partner to user 1
        self.user2_binding.main_partner_id = self.user
        expected_addresses = (
            partner
            | self._get_addresses(self.user2)
            | self._get_addresses(self.user, policy="public")
            | self.user
        )
        self._test_user_direct_child_of_company__parent_id(
            partner,
            self.user,
            expected_addresses=expected_addresses,
        )
        self.assertEqual(self.user3_binding.main_partner_id, self.user2)
        # Case 4: User 3 sees only its own records, the ones from its main partner,
        # and the publicly shared ones from their sibilings
        partner = self.user3
        expected_addresses = (
            partner
            | self._get_addresses(self.user3)
            | self._get_addresses(self.user2, policy="public")
            | self.user2
        )
        self._test_user_direct_child_of_company__parent_id(
            partner,
            self.user2,
            expected_addresses=expected_addresses,
        )
        # Case 5: Change User 3's main partner to company
        self.user3_binding.main_partner_id = self.company
        expected_addresses = (
            partner
            | self.company
            | self._get_addresses(self.company, policy="public")
            | self._get_addresses(self.user3, policy="private")
            | self.all_public_addresses
        )
        self._test_user_direct_child_of_company__parent_id(
            partner, self.company, expected_addresses=expected_addresses
        )
