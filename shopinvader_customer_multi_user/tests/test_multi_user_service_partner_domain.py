# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestMultiUserCommon


class TestMultiUserServicePartnerDomain(TestMultiUserCommon):
    """Test partner domains for services
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Enable multi-user
        cls.backend.customer_multi_user = True
        cls.all_bindings = (
            cls.user_binding + cls.user_binding2 + cls.user_binding3
        )
        # Create sale orders per each partner
        cls.sale_company = cls.env.ref("shopinvader.sale_order_2").copy(
            {"partner_id": cls.company.id}
        )
        cls.sale_user1 = cls.sale_company.copy(
            {"partner_id": cls.user_binding.record_id.id}
        )
        cls.sale_user2 = cls.sale_company.copy(
            {"partner_id": cls.user_binding2.record_id.id}
        )
        cls.sale_user3 = cls.sale_company.copy(
            {"partner_id": cls.user_binding3.record_id.id}
        )
        cls.all_orders = (
            cls.sale_company + cls.sale_user1 + cls.sale_user2 + cls.sale_user3
        )
        # Create invoices per each order/partner
        cls.all_invoices = cls.env["account.move"].browse()
        for sale in cls.all_orders:
            sale.action_confirm()
            for line in sale.order_line:
                line.write({"qty_delivered": line.product_uom_qty})
            cls.all_invoices |= sale._create_invoices()

        # Create address per each partner
        cls.address_company = cls.env["res.partner"].create(
            {
                "parent_id": cls.company.id,
                "type": "delivery",
                "name": "Delivery Address Company",
            }
        )
        cls.address_user1 = cls.env["res.partner"].create(
            {
                "parent_id": cls.user_binding.record_id.id,
                "type": "delivery",
                "name": "Delivery Address User 1",
            }
        )
        cls.address_user2 = cls.env["res.partner"].create(
            {
                "parent_id": cls.user_binding2.record_id.id,
                "type": "delivery",
                "name": "Delivery Address User 2",
            }
        )
        cls.address_user3 = cls.env["res.partner"].create(
            {
                "parent_id": cls.user_binding3.record_id.id,
                "type": "delivery",
                "name": "Delivery Address User 3",
            }
        )
        cls.all_addresses = (
            cls.address_company
            + cls.address_user1
            + cls.address_user2
            + cls.address_user3
        )

    def _get_service(self, partner, usage):
        with self.work_on_services(
            partner=partner.get_shop_partner(self.backend),
            partner_user=partner,
            shopinvader_session=self.shopinvader_session,
        ) as work:
            return work.component(usage=usage)

    def _test_address(self, partner, expected):
        service = self._get_service(partner, "addresses")
        res = service.search(per_page=100)
        expected = expected.sorted(key="id")
        found = sorted(res["data"], key=lambda x: x["id"])
        self.assertEqual(
            [x["id"] for x in found],
            expected.ids,
            """
            For partner:
                {partner.name}
            Expected:
                {expected}
            Found:
                {found}
            """.format(
                partner=partner,
                expected=" + ".join(
                    ["%s (%d)" % (x.name, x.id) for x in expected]
                ),
                found=" + ".join(
                    ["%s (%d)" % (x["name"], x["id"]) for x in found]
                ),
            ),
        )

    def _test_sale(self, partner, expected):
        service = self._get_service(partner, "sales")
        res = service.search()
        self.assertEqual(
            sorted([x["id"] for x in res["data"]]), sorted(expected.ids),
        )

    def _test_invoice(self, partner, expected):
        service = self._get_service(partner, "invoice")
        res = service._get_available_invoices()
        self.assertEqual(sorted(res.ids), sorted(expected.ids))

    # Company can see always everything
    def test_user_company__record_id(self):
        partner = self.company
        self._test_address(
            partner,
            partner
            + self.all_addresses
            + self.all_bindings.mapped("record_id"),
        )
        self._test_sale(partner, self.all_orders)
        self._test_invoice(partner, self.all_invoices)

    def test_user_company__parent_id(self):
        self.backend.multi_user_records_policy = "parent_id"
        partner = self.company
        self._test_address(
            partner,
            partner
            + self.all_addresses
            + self.all_bindings.mapped("record_id"),
        )
        self._test_sale(partner, self.all_orders)
        self._test_invoice(partner, self.all_invoices)

    def test_user_company__main_partner_id(self):
        self.backend.multi_user_records_policy = "main_partner_id"
        partner = self.company
        self._test_address(
            partner,
            partner
            + self.all_addresses
            + self.all_bindings.mapped("record_id"),
        )
        self._test_sale(partner, self.all_orders)
        self._test_invoice(partner, self.all_invoices)

    def _test_user_direct_child_of_company__record_id(
        self, partner, expected_addresses=None
    ):
        self._test_address(
            partner,
            partner
            + partner.child_ids.filtered(lambda x: not x.shopinvader_bind_ids),
        )
        self._test_sale(
            partner,
            self.all_orders.filtered(lambda x: x.partner_id == partner),
        )
        self._test_invoice(
            partner,
            self.all_orders.filtered(lambda x: x.partner_id == partner).mapped(
                "invoice_ids"
            ),
        )

    def test_user_direct_child_of_company__record_id(self):
        """Direct child sees only its own records.
        """
        partner = self.user_binding.record_id
        self._test_user_direct_child_of_company__record_id(partner)
        partner = self.user_binding2.record_id
        self._test_user_direct_child_of_company__record_id(partner)
        partner = self.user_binding3.record_id
        self._test_user_direct_child_of_company__record_id(partner)

    def _test_user_direct_child_of_company__parent_id(
        self, partner, parent_partners, expected_addresses=None
    ):
        expected_addresses = expected_addresses or partner + parent_partners
        expected_sales = self.all_orders.filtered(
            lambda x: x.partner_id in partner + parent_partners
        )
        expected_invoices = expected_sales.mapped("invoice_ids")
        self._test_address(partner, expected_addresses)
        self._test_sale(partner, expected_sales)
        self._test_invoice(partner, expected_invoices)

    def test_user_direct_child_of_company__parent_id(self):
        """Direct child sees only its own records and the ones from direct parent.
        """
        self.backend.multi_user_records_policy = "parent_id"
        partner = self.user_binding.record_id
        expected_addresses = (
            self.company + self.address_company + partner + self.address_user1
        )
        self._test_user_direct_child_of_company__parent_id(
            partner, self.company, expected_addresses=expected_addresses
        )
        partner = self.user_binding2.record_id
        expected_addresses = (
            self.company + self.address_company + partner + self.address_user2
        )
        self._test_user_direct_child_of_company__parent_id(
            partner, self.company, expected_addresses=expected_addresses
        )
        partner = self.user_binding3.record_id
        expected_addresses = (
            partner
            + self.address_user3
            + self.user_binding2.record_id
            + self.address_user2
        )
        self._test_user_direct_child_of_company__parent_id(
            partner,
            self.user_binding2.record_id,
            expected_addresses=expected_addresses,
        )
        # main partner is the parent in this case
        # but if we set the company, then they can see records from the company as well
        self.user_binding3.main_partner_id = self.company
        expected_addresses += self.company + self.address_company
        # self.user_binding3.with_context(foo=1)._make_address_domain()
        self._test_user_direct_child_of_company__parent_id(
            partner,
            self.company + self.user_binding2.record_id,
            expected_addresses=expected_addresses,
        )

    def test_user_direct_child_of_company__main_partner_id(self):
        """Direct child sees only its own records and the ones from main partner.
        """
        self.backend.multi_user_records_policy = "main_partner_id"

        partner = self.user_binding.record_id
        expected_addresses = (
            self.company + self.address_company + partner + self.address_user1
        )
        self._test_user_direct_child_of_company__parent_id(
            partner, self.company, expected_addresses=expected_addresses
        )

        partner = self.user_binding2.record_id
        expected_addresses = (
            self.company + self.address_company + partner + self.address_user2
        )
        self._test_user_direct_child_of_company__parent_id(
            partner, self.company, expected_addresses=expected_addresses
        )

        # Change main partner to user 1
        self.user_binding2.main_partner_id = self.user_binding.record_id
        expected_addresses = (
            partner
            + self.address_user2
            + self.address_user1
            + self.user_binding.record_id
        )
        self._test_user_direct_child_of_company__parent_id(
            partner,
            self.user_binding.record_id,
            expected_addresses=expected_addresses,
        )
        self.assertEqual(
            self.user_binding3.main_partner_id, self.user_binding2.record_id
        )
        partner = self.user_binding3.record_id
        expected_addresses = (
            partner
            + self.address_user3
            + self.user_binding2.record_id
            + self.address_user2
        )
        self._test_user_direct_child_of_company__parent_id(
            partner,
            self.user_binding2.record_id,
            expected_addresses=expected_addresses,
        )
        # Change main partner to company
        self.user_binding3.main_partner_id = self.company
        expected_addresses = (
            self.company + self.address_company + partner + self.address_user3
        )
        self._test_user_direct_child_of_company__parent_id(
            partner, self.company, expected_addresses=expected_addresses
        )
