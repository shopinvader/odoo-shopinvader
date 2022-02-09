# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_customer_multi_user.tests.common import (
    TestMultiUserPartnerDomainCommon,
)


class TestMultiUserCompanyGroupCommon(TestMultiUserPartnerDomainCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # `TestMultiUserPartnerDomainCommon` will give us this hierarchy:
        #
        #      ┌─ Company ─┐
        #      │           │
        #      ▼           ▼
        #    User        User2
        #                  │
        #                  ▼
        #                User3
        #
        # Create a company group, move the existing company to the group
        # and create a second company also part of the group.
        #
        #           ┌─── Company Group ───┐
        #           │          │          │
        #           │          │          │
        #           │          ▼          │
        #           │        User6        │
        #           ▼                     ▼
        #     ┌─ Company ─┐        ┌─ Company 2 ─┐
        #     │           │        │             │
        #     ▼           ▼        ▼             ▼
        #   User        User2    User4         User5
        #                 │
        #                 ▼
        #               User3
        #
        cls.company_group, cls.company_group_binding = cls._create_partner_and_binding(
            name="Company Group Corp", is_company=True
        )
        cls.company.company_group_id = cls.company_group
        cls.company2, cls.company2_binding = cls._create_partner_and_binding(
            name="Smile Inc",
            is_company=True,
            company_group_id=cls.company_group.id,
        )
        cls.user4, cls.user4_binding = cls._create_partner_and_binding(
            name="User 4",
            parent_id=cls.company2.id,
        )
        cls.user5, cls.user5_binding = cls._create_partner_and_binding(
            name="User 5",
            parent_id=cls.company2.id,
        )
        cls.user6, cls.user6_binding = cls._create_partner_and_binding(
            name="User 6",
            parent_id=cls.company_group.id,
        )
        # Update shortcuts and create orders and addresses for each
        new_companies = cls.company_group + cls.company2
        new_users = cls.user4 + cls.user5 + cls.user6
        new_partners = new_companies + new_users
        cls.all_companies += new_companies
        cls.all_users += new_users
        cls.all_partners += new_partners
        # Create Sale Orders and Invoices for each new partner
        cls.all_orders += cls._create_sales_and_invoices(new_partners)
        cls.all_invoices = cls.all_orders.invoice_ids
        # Create Private and Public addresses for each new partner
        new_public_addresses, new_private_addresses = cls._create_addresses(
            new_partners
        )
        cls.all_public_addresses += new_public_addresses
        cls.all_private_addresses += new_private_addresses
        cls.all_addresses = cls.all_public_addresses + cls.all_private_addresses
        # Shortcuts for company addresses, users, etc
        cls.company_users = cls.user + cls.user2 + cls.user3
        cls.company_partners = cls.company + cls.company_users
        cls.company_orders = cls.all_orders.filtered(
            lambda x: x.partner_id in cls.company_partners
        )

        cls.company2_users = cls.user4 + cls.user5
        cls.company2_partners = cls.company2 + cls.company2_users
        cls.company2_orders = cls.all_orders.filtered(
            lambda x: x.partner_id in cls.company2_partners
        )
