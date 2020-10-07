# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestMultiUserCommon


class TestMultiUserServicePartnerDomain(TestMultiUserCommon):
    """Test partner domains for services
    """

    def _get_service(self, partner, usage):
        with self.work_on_services(
            partner=partner, shopinvader_session=self.shopinvader_session
        ) as work:
            return work.component(usage=usage)

    def _test_domain(self, partner, expected_partner):
        # address
        service = self._get_service(partner, "addresses")
        domain = service._get_base_search_domain()
        self.assertEqual(domain, [("id", "child_of", expected_partner.id)])
        # sale
        service = self._get_service(partner, "sales")
        domain = service._get_base_search_domain()
        partner_leaf = [x for x in domain if x[0] == "partner_id"]
        self.assertEqual(
            partner_leaf, [("partner_id", "child_of", expected_partner.id)]
        )
        # invoice
        service = self._get_service(partner, "sales")
        domain = service._get_base_search_domain()
        partner_leaf = [x for x in domain if x[0] == "partner_id"]
        self.assertEqual(
            partner_leaf, [("partner_id", "child_of", expected_partner.id)]
        )
        # invoice
        service = self._get_service(partner, "invoice")
        domain = service._get_sale_order_domain()
        partner_leaf = [x for x in domain if x[0] == "partner_id"]
        self.assertEqual(
            partner_leaf, [("partner_id", "child_of", expected_partner.id)]
        )

    def test_user_partner_company(self):
        self.assertEqual(self.backend.multi_user_records_policy, "record_id")
        partner = self.company
        self._test_domain(partner, partner)

    def test_user_partner_simple_user(self):
        partner = self.user_binding.record_id
        self._test_domain(partner, partner)

    def test_parent_partner_company(self):
        self.backend.multi_user_records_policy = "parent_id"
        partner = self.company
        self._test_domain(partner, partner)

    def test_parent_partner_simple_user(self):
        self.backend.multi_user_records_policy = "parent_id"
        partner = self.user_binding.record_id
        self._test_domain(partner, self.company)

    def test_main_partner_company(self):
        self.backend.multi_user_records_policy = "main_partner_id"
        partner = self.company
        self._test_domain(partner, partner)

    def test_main_partner_simple_user(self):
        self.backend.multi_user_records_policy = "main_partner_id"
        partner = self.user_binding.record_id
        self._test_domain(partner, self.company)
