# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestMultiUserCompanyGroupCommon


class TestMultiUserRecordsHierarchy(TestMultiUserCompanyGroupCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend.multi_user_records_policy = "main_partner_id"
        cls.backend.multi_user_company_group_records_policy = "hierarchy"
        cls.backend.multi_user_company_group_address_policy = "hierarchy"

    def test_hierarchy_company_group__company(self):
        """The company group sees everything"""
        self._test_partner_records(
            self.company_group,
            addresses=self.all_partners + self.all_addresses,
            orders=self.all_orders,
        )

    def test_hierarchy_company_group__user(self):
        """The company group users sees everything that's public"""
        order_partner_ids = [
            self.company_group.id,
            self.company.id,
            self.company2.id,
            self.user6.id,
        ]
        orders = self.all_orders.filtered(
            lambda o: o.partner_id.id in order_partner_ids
        )
        self._test_partner_records(
            self.user6,
            addresses=(
                self.user6
                | self.company_group
                | self.all_public_addresses
                | self._get_addresses(self.user6, policy="private")
            ),
            orders=orders,
        )

    def test_hierarchy_company__company(self):
        """The company sees only its own records"""
        self._test_partner_records(
            self.company,
            addresses=(
                self.company_partners | self._get_addresses(self.company_partners)
            ),
            orders=self.company_orders,
        )

    def test_hierarchy_company__user(self):
        """The company users sees its company records and public addresses"""
        self._test_user_direct_child_of_company__parent_id(
            self.user,
            self.company,
            expected_addresses=(
                self.user
                | self.company
                | self._get_addresses(self.user)
                | self._get_addresses(self.company, policy="public")
                | self._get_addresses(self.company_users, policy="public")
            ),
        )

    def test_hierarchy_company_with_child__company(self):
        """The company sees only its own records and its childs records"""
        self.company2.parent_id = self.company
        self._test_partner_records(
            self.company,
            addresses=(
                self.company_partners
                | self.company2_partners
                | self._get_addresses(self.company_partners)
                | self._get_addresses(self.company2_partners)
            ),
            orders=(self.company_orders | self.company2_orders),
        )

    def test_hierarchy_company_with_child__user(self):
        """The company user sees only its company records and public addresses"""
        self.company2.parent_id = self.company
        self._test_user_direct_child_of_company__parent_id(
            self.user,
            self.company,
            expected_addresses=(
                self.user
                | self.company
                | self._get_addresses(self.user)
                | self._get_addresses(self.company_partners, policy="public")
                | self._get_addresses(self.company2_partners, policy="public")
            ),
        )


class TestMultiUserRecordsShared(TestMultiUserCompanyGroupCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend.multi_user_records_policy = "main_partner_id"
        cls.backend.multi_user_company_group_records_policy = "shared"
        cls.backend.multi_user_company_group_address_policy = "shared"

    def test_shared_company_group__company(self):
        """The company group sees everything"""
        # Exactly the same than "hierarchy", as the group users always see everything
        self._test_partner_records(
            self.company_group,
            addresses=self.all_partners + self.all_addresses,
            orders=self.all_orders,
        )

    def test_shared_company_group__user(self):
        """The company group users sees everything that's public"""
        # Exactly the same than "hierarchy", as the group users always see everything
        order_partner_ids = [
            self.company_group.id,
            self.company.id,
            self.company2.id,
            self.user6.id,
        ]
        orders = self.all_orders.filtered(
            lambda o: o.partner_id.id in order_partner_ids
        )
        self._test_partner_records(
            self.user6,
            addresses=(
                self.user6
                | self.company_group
                | self.all_public_addresses
                | self._get_addresses(self.user6, policy="private")
            ),
            orders=orders,
        )

    def test_shared_company__company(self):
        """The company sees everything that's public in the group"""
        order_partner_ids = [
            # orders linked directly to companies
            self.company_group.id,
            self.company.id,
            self.company2.id,
            # and its own users
            *self.company_users.ids,
        ]
        orders = self.all_orders.filtered(
            lambda o: o.partner_id.id in order_partner_ids
        )
        self._test_partner_records(
            self.company,
            addresses=(
                self.company
                | self.company_users
                | self.all_public_addresses
                | self._get_addresses(self.company)
                | self._get_addresses(self.company_users)
            ),
            orders=orders,
        )

    def test_shared_company__user(self):
        """The company users sees everything that's public in the group"""
        order_partner_ids = [
            # orders linked directly to companies
            self.company_group.id,
            self.company.id,
            self.company2.id,
            # and his own orders
            self.user.id,
        ]
        orders = self.all_orders.filtered(
            lambda o: o.partner_id.id in order_partner_ids
        )
        self._test_partner_records(
            self.user,
            addresses=(
                self.user
                | self.company
                | self._get_addresses(self.user)
                | self.all_public_addresses
            ),
            orders=orders,
        )


class TestMultiUserRecordsMixed(TestMultiUserCompanyGroupCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend.multi_user_records_policy = "main_partner_id"
        cls.backend.multi_user_company_group_records_policy = "hierarchy"
        cls.backend.multi_user_company_group_address_policy = "shared"

    def test_mixed_company_group__company(self):
        """The company group sees everything"""
        self._test_partner_records(
            self.company_group,
            addresses=self.all_partners + self.all_addresses,
            orders=self.all_orders,
        )

    def test_mixed_company_group__user(self):
        """The company group users sees everything that's public"""
        order_partner_ids = [
            self.company_group.id,
            self.company.id,
            self.company2.id,
            self.user6.id,
        ]
        orders = self.all_orders.filtered(
            lambda o: o.partner_id.id in order_partner_ids
        )
        self._test_partner_records(
            self.user6,
            addresses=(
                self.user6
                | self.company_group
                | self.all_public_addresses
                | self._get_addresses(self.user6, policy="private")
            ),
            orders=orders,
        )

    def test_mixed_company__company(self):
        """The company sees only its own records, but all public addresses"""
        self._test_partner_records(
            self.company,
            addresses=(
                self.company
                | self.company_users
                | self.all_public_addresses
                | self._get_addresses(self.company)
                | self._get_addresses(self.company_users)
            ),
            orders=self.company_orders,
        )

    def test_mixed_company__user(self):
        """The company users sees its company records and public addresses"""
        self._test_user_direct_child_of_company__parent_id(
            self.user,
            self.company,
            expected_addresses=(
                self.user
                | self.company
                | self._get_addresses(self.user)
                | self.all_public_addresses
            ),
        )
