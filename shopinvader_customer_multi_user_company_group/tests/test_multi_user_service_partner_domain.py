# Copyright 2021 Camptocamp (http://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon


class TestMultiUserServicePartnerDomain(TestCustomerCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Enable multi-user
        cls.backend.customer_multi_user = True
        # Create companies
        cls.company_group_binding = cls._create_partner(
            cls.env,
            name="Company Group",
            external_id="company-group",
            email="info@company-group.org",
            is_company=True,
        )
        cls.company_a_binding = cls._create_partner(
            cls.env,
            name="Company A",
            external_id="company-a",
            email="info@company-a.org",
            invader_user_token="COMPANY_A_TOKEN",
            company_group_id=cls.company_group_binding.record_id.id,
            is_company=True,
        )
        cls.company_b_binding = cls._create_partner(
            cls.env,
            name="Company B",
            external_id="company-b",
            email="info@company-b.org",
            invader_user_token="COMPANY_B_TOKEN",
            company_group_id=cls.company_group_binding.record_id.id,
            is_company=True,
        )
        # Create users
        cls.user_g_binding = cls._create_partner(
            cls.env,
            name="User G",
            external_id="user-g",
            email="user-g@company-group.org",
            parent_id=cls.company_group_binding.record_id.id,
        )
        cls.user_a_binding = cls._create_partner(
            cls.env,
            name="User A",
            external_id="user-a",
            email="user-a@company-a.org",
            parent_id=cls.company_a_binding.record_id.id,
        )
        cls.user_b_binding = cls._create_partner(
            cls.env,
            name="User B",
            external_id="user-b",
            email="user-b@company-b.org",
            parent_id=cls.company_b_binding.record_id.id,
        )
        cls.company_group = cls.company_group_binding.record_id
        cls.company_a = cls.company_a_binding.record_id
        cls.company_b = cls.company_b_binding.record_id
        cls.user_g = cls.user_g_binding.record_id
        cls.user_a = cls.user_a_binding.record_id
        cls.user_b = cls.user_b_binding.record_id
        # Some quick recordset accessors
        cls.all_companies = cls.company_group + cls.company_a + cls.company_b
        cls.all_users = cls.user_g + cls.user_a + cls.user_b
        cls.all_partners = cls.all_companies + cls.all_users
        # Create Sale Orders per each user
        # For maintenance reasons, loop and setattr on the fly
        cls.all_sales = cls.env["sale.order"]
        base_sale_order = cls.env.ref("shopinvader.sale_order_2")
        for partner in cls.all_users:
            partner_key = partner.name.lower().replace(" ", "_")
            sale = base_sale_order.copy({"partner_id": partner.id})
            setattr(cls, f"sale_{partner_key}", sale)
            cls.all_sales |= sale
        # Create invoices per each order
        cls.all_invoices = cls.env["account.move"]
        for sale in cls.all_sales:
            sale.action_confirm()
            for line in sale.order_line:
                line.write({"qty_delivered": line.product_uom_qty})
            cls.all_invoices |= sale._create_invoices()
        # Create public and private addresses for each user
        # For maintenance reasons, loop and setattr on the fly
        ResPartner = cls.env["res.partner"]
        cls.all_public_addresses = cls.env["res.partner"]
        cls.all_private_addresses = cls.env["res.partner"]
        for partner in cls.all_partners:
            partner_key = partner.name.lower().replace(" ", "_")
            public_address = ResPartner.create(
                {
                    "name": f"Delivery Address {partner.name} (Public)",
                    "parent_id": partner.id,
                    "type": "delivery",
                    "invader_address_share_policy": "public",
                }
            )
            private_address = ResPartner.create(
                {
                    "name": f"Delivery Address {partner.name} (Private)",
                    "parent_id": partner.id,
                    "type": "delivery",
                    "invader_address_share_policy": "private",
                }
            )
            setattr(cls, f"address_{partner_key}_public", public_address)
            setattr(cls, f"address_{partner_key}_private", private_address)
            cls.all_public_addresses |= public_address
            cls.all_private_addresses |= private_address
        cls.all_addresses = cls.all_public_addresses + cls.all_private_addresses

    @staticmethod
    def _create_partner(env, **kw):
        values = {
            "backend_id": env.ref("shopinvader.backend_1").id,
            "name": "ACME ltd",
            "external_id": "acme",
            "email": "company@test.com",
            "ref": "#ACME",
        }
        values.update(kw)
        return env["shopinvader.partner"].create(values)

    @staticmethod
    def _get_partner_expected_versus_found_message(
        partner, expected, found, mapper=None
    ):
        if mapper is None:

            def mapper(x):
                return "%s (%d)" % (x.name, x.id)

        return """
            For partner:
                {partner}
            Expected:
                {expected}
            Found:
                {found}
            """.format(
            partner=partner.name,
            expected=("\n" + " " * 16).join(expected.mapped(mapper)),
            found=("\n" + " " * 16).join(found.mapped(mapper)),
        )

    def _get_service(self, partner, usage):
        with self.work_on_services(
            partner=partner.get_shop_partner(self.backend),
            partner_user=partner,
            shopinvader_session=self.shopinvader_session,
        ) as work:
            return work.component(usage=usage)

    # Test Helpers

    def _test_address(self, partner, expected):
        service = self._get_service(partner, "addresses")
        res = service.search(per_page=100)
        res_ids = [x["id"] for x in res["data"]]
        found = self.env[expected._name].browse(res_ids).sorted(key="id")
        expected = expected.sorted(key="id")
        self.assertEqual(
            found.ids,
            expected.ids,
            self._get_partner_expected_versus_found_message(partner, expected, found),
        )

    def _test_sale(self, partner, expected):
        service = self._get_service(partner, "sales")
        res = service.search()
        res_ids = [x["id"] for x in res["data"]]
        found = self.env[expected._name].browse(res_ids).sorted(key="id")
        expected = expected.sorted(key="id")
        self.assertEqual(
            found.ids,
            expected.ids,
            self._get_partner_expected_versus_found_message(
                partner,
                expected,
                found,
                mapper=lambda x: "%s (%d) :: %s (%d)"
                % (x.name, x.id, x.partner_id.name, x.partner_id.id),
            ),
        )

    def _test_invoice(self, partner, expected):
        service = self._get_service(partner, "invoice")
        found = service._get_available_invoices().sorted(key="id")
        expected = expected.sorted(key="id")
        self.assertEqual(
            found.ids,
            expected.ids,
            self._get_partner_expected_versus_found_message(
                partner,
                expected,
                found,
                mapper=lambda x: "%s (%d) :: %s (%d)"
                % (x.name, x.id, x.partner_id.name, x.partner_id.id),
            ),
        )

    # Tests

    def test_company_group_level(self):
        """The company group sees all"""
        # Case 1: The company group itself
        partner = self.company_group
        self._test_address(partner, self.all_partners + self.all_addresses)
        self._test_sale(partner, self.all_sales)
        self._test_invoice(partner, self.all_invoices)
        # Case 2: The company group user, same but only public addresses
        partner = self.user_g
        self._test_address(
            partner,
            (
                self.user_g
                | self.company_group
                | self.all_public_addresses
                | self.address_user_g_private
            ),
        )
        self._test_sale(partner, self.all_sales)
        self._test_invoice(partner, self.all_invoices)

    def test_company_level(self):
        """The company sees only its own records"""
        # Case 1: Company A
        partner = self.company_a
        self._test_address(
            partner,
            (
                partner
                | self.user_a
                | self.address_user_a_public
                | self.address_user_a_private
                | self.address_company_a_public
                | self.address_company_a_private
            ),
        )
        sales = self.sale_user_a
        self._test_sale(partner, sales)
        self._test_invoice(partner, sales.mapped("invoice_ids"))
        # Case 2: Same but without admin user
        partner = self.user_a
        self._test_address(
            partner,
            (
                partner
                | self.company_a
                | self.address_user_a_public
                | self.address_user_a_private
                | self.address_company_a_public
            ),
        )
        sales = self.sale_user_a
        self._test_sale(partner, sales)
        self._test_invoice(partner, sales.mapped("invoice_ids"))

    def test_company_level_with_child(self):
        """The company sees only its own records and its childs records"""
        self.company_b.parent_id = self.company_a
        # Case 1: Company A
        partner = self.company_a
        self._test_address(
            partner,
            (
                # Sees company A
                self.company_a
                | self.user_a
                | self.address_user_a_public
                | self.address_user_a_private
                | self.address_company_a_public
                | self.address_company_a_private
                # And company B
                | self.company_b
                | self.user_b
                | self.address_user_b_public
                | self.address_user_b_private
                | self.address_company_b_public
                | self.address_company_b_private
            ),
        )
        sales = self.sale_user_a | self.sale_user_b
        self._test_sale(partner, sales)
        self._test_invoice(partner, sales.mapped("invoice_ids"))
        # Case 2: Same but without admin user
        partner = self.user_a
        self._test_address(
            partner,
            (
                # Sees company A
                self.company_a
                | self.user_a
                | self.address_user_a_public
                | self.address_user_a_private
                | self.address_company_a_public
                # And company B
                | self.address_user_b_public
                | self.address_company_b_public
            ),
        )
        sales = self.sale_user_a
        self._test_sale(partner, sales)
        self._test_invoice(partner, sales.mapped("invoice_ids"))
