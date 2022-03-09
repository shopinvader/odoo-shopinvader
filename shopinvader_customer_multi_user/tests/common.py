# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from functools import partial
from os import urandom
from textwrap import dedent

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon


class TestMultiUserCommon(TestCustomerCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company, cls.company_binding = cls._create_partner_and_binding(
            name="ACME Ltd", invader_user_token="ABCDEF", is_company=True
        )
        cls.user, cls.user_binding = cls._create_partner_and_binding(
            name="Simple user",
            parent_id=cls.company.id,
        )
        # Create 2 more users so that we have 1 company user with 3 simple
        # users and user 3 is a child of user 2.
        #
        #      ┌─ Company ─┐
        #      │           │
        #      ▼           ▼
        #    User        User2
        #                  │
        #                  ▼
        #                User3
        #
        cls.user2, cls.user2_binding = cls._create_partner_and_binding(
            name="Simple user 2",
            parent_id=cls.company.id,
        )
        cls.user3, cls.user3_binding = cls._create_partner_and_binding(
            name="Simple user 3",
            parent_id=cls.user2.id,
            main_partner_id=cls.user2.id,
        )
        # Configure backend
        cls.backend.multi_user_records_policy = "record_id"
        cls.backend.customer_multi_user = True

    @classmethod
    def _create_partner_binding(cls, **vals):
        """Creates a shopinvader.partner"""
        assert "name" in vals, "name is required"
        if "backend_id" not in vals:
            vals["backend_id"] = cls.backend.id
        if "external_id" not in vals:
            vals["external_id"] = vals["name"].lower().replace(" ", "-")
            vals["external_id"] += str(abs(hash(urandom(4))))
        if "ref" not in vals:
            vals["ref"] = "#%s" % vals["external_id"].upper()
        if "email" not in vals:
            vals["email"] = "%s@example.com" % vals["external_id"]
        return cls.env["shopinvader.partner"].create(vals)

    @classmethod
    def _create_partner(cls, **vals):
        """Creates a shopinvader.partner, returns the related res.partner"""
        return cls._create_partner_binding(**vals).record_id

    @classmethod
    def _create_partner_and_binding(cls, **vals):
        """Creates a shopinvader.partner, returns both binding and res.partner"""
        binding = cls._create_partner_binding(**vals)
        return binding.record_id, binding

    def _get_service(self, partner, usage="users"):
        with self.work_on_services(
            partner=partner, shopinvader_session=self.shopinvader_session
        ) as work:
            return work.component(usage=usage)


class TestUserManagementCommmon(TestMultiUserCommon):
    """Test interaction with /users endpoint."""

    def _get_service(self, partner, usage="users"):
        with self.work_on_services(partner=partner) as work:
            return work.component(usage=usage)

    def _test_search(self, service, expected):
        _res = sorted(service.dispatch("search")["data"], key=lambda x: x["email"])
        self.assertEqual(
            _res,
            [
                {
                    "email": x.email,
                    "id": x.id,
                    "name": x.name,
                    "parent_id": x.parent_id.id,
                    "can_manage_users": x.can_manage_users,
                }
                for x in expected.sorted("email")
            ],
        )

    def _test_create(self, service, params, parent=None):
        partner = parent or service.partner_user
        count_before = len(partner.child_ids)
        res = service.dispatch("create", params=params)["data"]
        self.assertEqual(len(partner.child_ids), count_before + 1)
        new_partner = partner.child_ids.filtered_domain(
            [("email", "=", params["email"])]
        )
        invader_partner = new_partner._get_invader_partner(self.backend)
        expected = dict(
            params,
            parent_id=partner.id,
            id=invader_partner.id,
            can_manage_users=invader_partner.can_manage_users,
        )
        self.assertEqual(res, expected)
        return invader_partner


class TestMultiUserPartnerDomainCommon(TestMultiUserCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Quick shortcuts
        cls.all_companies = cls.company
        cls.all_users = cls.user + cls.user2 + cls.user3
        cls.all_partners = cls.all_companies + cls.all_users
        # Create Sale Orders and Invoices for each partner
        cls.all_orders = cls._create_sales_and_invoices(cls.all_partners)
        cls.all_invoices = cls.all_orders.invoice_ids
        # Create Private and Public addresses for each partner
        cls.all_public_addresses, cls.all_private_addresses = cls._create_addresses(
            cls.all_partners
        )
        cls.all_addresses = cls.all_public_addresses + cls.all_private_addresses

    @classmethod
    def _create_sales_and_invoices(cls, partners, invoice=True):
        base_sale_order = cls.env.ref("shopinvader.sale_order_2")
        sales = cls.env["sale.order"]
        for partner in partners:
            sale = base_sale_order.copy({"partner_id": partner.id})
            sale.action_confirm()
            if invoice:
                for line in sale.order_line:
                    line.write({"qty_delivered": line.product_uom_qty})
                sale._create_invoices()
            sales += sale
        return sales

    @classmethod
    def _create_addresses(cls, partners, public=True, private=True):
        """Creates both public and private addresses for partners

        :param public: if True, create public addresses
        :param private: if True, create private addresses
        :return: a tuple of public and private addresses
        """
        res_public = cls.env["res.partner"]
        res_private = cls.env["res.partner"]
        for partner in partners:
            if public:
                res_public += cls.env["res.partner"].create(
                    {
                        "name": f"{partner.name} (Public Address)",
                        "parent_id": partner.id,
                        "type": "delivery",
                        "invader_address_share_policy": "public",
                    }
                )
            if private:
                res_private += cls.env["res.partner"].create(
                    {
                        "name": f"{partner.name} (Private Address)",
                        "parent_id": partner.id,
                        "type": "delivery",
                        "invader_address_share_policy": "private",
                    }
                )
        return res_public, res_private

    @classmethod
    def _get_addresses(cls, partners, policy=None):
        """Return partner direct children addresses

        :param policy: Optional. Either 'public' or 'private' or None
        """
        addresses = partners.child_ids.filtered(
            lambda rec: not rec.shopinvader_bind_ids
        )
        if policy:
            addresses = addresses.filtered(
                lambda rec: rec.invader_address_share_policy == policy
            )
        return addresses

    def _partner_diff_message(self, partner, expected, found, display_format=None):
        """Build a beautiful human readable recordset diff message

        :param partner: the partner we're testing
        :param expected: the expected result recordset
        :param found: the found result recordset
        :param display_format: the format to use to print each record (optional)
        """

        def mapper(record, compare=None):
            mark = " "
            if compare:
                mark = " " if record in compare else "✗"
            if display_format:
                record_format = display_format
            else:
                record_format = "({rec.id}) {rec.display_name}"
                if record._name != "res.partner" and "partner_id" in record._fields:
                    record_format += (
                        " | ({rec.partner_id.id}) {rec.partner_id.display_name}"
                    )
            return f"{mark} {record_format.format(rec=record)}"

        def records2str(records, compare=None):
            return "\n".join(records.mapped(partial(mapper, compare=compare)))

        return dedent(
            """
            For partner:
            > {partner}

            Expected:
            {expected}

            Found:
            {found}
            """
        ).format(
            partner=f"({partner.id}) {partner.display_name}",
            expected=records2str(expected, compare=found),
            found=records2str(found, compare=expected),
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
        res_ids = [x["id"] for x in res["data"]]
        found = self.env[expected._name].browse(res_ids).sorted(key="id")
        expected = expected.sorted(key="id")
        self.assertEqual(
            found.ids,
            expected.ids,
            self._partner_diff_message(partner, expected, found),
        )

    def _test_sale(self, partner, expected):
        service = self._get_service(partner, "sales")
        res = service.search(per_page=1000)
        res_ids = [x["id"] for x in res["data"]]
        found = self.env[expected._name].browse(res_ids).sorted(key="id")
        expected = expected.sorted(key="id")
        self.assertEqual(
            found.ids,
            expected.ids,
            self._partner_diff_message(partner, expected, found),
        )

    def _test_invoice(self, partner, expected):
        service = self._get_service(partner, "invoice")
        found = service._get_available_invoices().sorted(key="id")
        expected = expected.sorted(key="id")
        self.assertEqual(
            found.ids,
            expected.ids,
            self._partner_diff_message(partner, expected, found),
        )

    def _test_partner_records(
        self, partner, addresses=None, orders=None, invoices=None
    ):
        """Test everything for a partner

        :param partner: res.partner to test
        :param addresses: expected addresses recordset
        :param orders: expected sales orders recordset
        :param invoices: expected invoices recordset
        """
        if addresses is not None:
            self._test_address(partner, addresses)
        if orders is not None:
            self._test_sale(partner, orders)
        if invoices is not None:
            self._test_invoice(partner, invoices)
        elif orders:
            self._test_invoice(partner, orders.invoice_ids)

    def _test_user_direct_child_of_company__record_id(self, partner):
        """Helper to check company direct children users (record_id)"""
        self._test_partner_records(
            partner,
            addresses=partner + self._get_addresses(partner),
            orders=self.all_orders.filtered(lambda x: x.partner_id == partner),
            invoices=self.all_orders.filtered(
                lambda x: x.partner_id == partner
            ).invoice_ids,
        )

    def _test_user_direct_child_of_company__parent_id(
        self, partner, parent_partners, expected_addresses=None
    ):
        """Helper to check company direct children users (parent_id)"""
        expected_addresses = expected_addresses or partner + parent_partners
        expected_sales = self.all_orders.filtered(
            lambda x: x.partner_id in (partner | parent_partners)
        )
        expected_invoices = expected_sales.invoice_ids
        self._test_partner_records(
            partner,
            addresses=expected_addresses,
            orders=expected_sales,
            invoices=expected_invoices,
        )
