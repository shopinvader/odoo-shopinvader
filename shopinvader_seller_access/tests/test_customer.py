import ast

from odoo.exceptions import AccessDenied, MissingError, UserError

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon

from .common import SellerGroupBackendMixin


class TestCustomer(SellerGroupBackendMixin, TestCustomerCommon):
    def test_get_available_customers(self):
        with self.seller_group():
            customers = self.service_with_partner.dispatch("available_customers")
        self.assertEquals(
            len(customers),
            self.env["res.partner"].search_count(
                ast.literal_eval(self.backend.seller_access_customer_domain)
            ),
        )
        self.assertEquals(
            tuple(customers[0].keys()),
            (
                "id",
                "name",
                "email",
                "street",
                "street2",
                "zip",
                "city",
                "state_id",
                "country_id",
                "parent_id",
            ),
        )

    def test_get_available_customers_no_seller_access(self):
        self.backend.seller_access = False
        with self.assertRaises(AccessDenied) as e:
            self.service_with_partner.dispatch("available_customers")
        self.assertEquals(
            str(e.exception), "This backend does not support seller access"
        )

    def test_get_available_customers_wrong_group(self):
        with self.assertRaises(AccessDenied) as e:
            with self.seller_group("buyer"):
                self.service_with_partner.dispatch("available_customers")
        self.assertEquals(
            str(e.exception), "seller group is required and not present in ['buyer']"
        )

    def test_get_available_customers_with_domain(self):
        self.backend.seller_access_customer_domain = '[("name", "ilike", "lo")]'
        with self.seller_group():
            customers = self.service_with_partner.dispatch("available_customers")
        self.assertEquals(len(customers), 2)
        self.assertEquals(
            {customer["name"] for customer in customers},
            {"Floyd Steward", "Lorraine Douglas"},
        )

    def test_update_available_customers_email(self):
        self.backend.seller_access_customer_domain = (
            '[("id", "=", %s)]' % self.partner_2.id
        )
        with self.seller_group():
            self.service_with_partner.dispatch(
                "update",
                self.partner_2.id,
                params={
                    "email": "new_email@shopinvader.com",
                },
            )
            self.assertEquals(self.partner_2.email, "new_email@shopinvader.com")

    def test_update_available_customers_email_unbound(self):
        unbound = self.env["res.partner"].create(
            {
                "name": "Unbound Partner",
                "email": "unbound@shopinvader.com",
            }
        )

        self.backend.seller_access_customer_domain = '[("id", ">=", %s)]' % unbound.id
        with self.seller_group():
            self.service_with_partner.dispatch(
                "update",
                unbound.id,
                params={
                    "email": "new_unbound_email@shopinvader.com",
                },
            )
            self.assertEquals(unbound.email, "new_unbound_email@shopinvader.com")

    def test_update_available_customers_email_wrong_partner(self):
        self.backend.seller_access_customer_domain = (
            '[("id", "!=", %s)]' % self.partner_2.id
        )
        with self.seller_group():
            with self.assertRaises(MissingError):
                self.service_with_partner.dispatch(
                    "update",
                    self.partner_2.id,
                    params={
                        "email": "new_email@shopinvader.com",
                    },
                )
        self.assertNotEquals(self.partner_2.email, "new_email@shopinvader.com")

    def test_update_available_customers_not_email(self):
        self.backend.seller_access_customer_domain = (
            '[("id", "=", %s)]' % self.partner_2.id
        )
        with self.seller_group():
            with self.assertRaises(UserError):
                self.service_with_partner.dispatch(
                    "update",
                    self.partner_2.id,
                    params={"email": "new_email@shopinvader.com", "name": "new_name"},
                )

        self.assertNotEquals(self.partner_2.email, "new_email@shopinvader.com")
        self.assertNotEquals(self.partner_2.name, "new_name")

    def test_update_available_customers_email_wrong_group(self):
        self.backend.seller_access_customer_domain = (
            '[("id", "==", %s)]' % self.partner_2.id
        )
        with self.seller_group("buyer"):
            with self.assertRaises(MissingError):
                self.service_with_partner.dispatch(
                    "update",
                    self.partner_2.id,
                    params={
                        "email": "new_email@shopinvader.com",
                    },
                )

        self.assertNotEquals(self.partner_2.email, "new_email@shopinvader.com")

    def test_get_available_customers_seller_access_customer_domain(self):
        self.backend.seller_access_customer_domain = '[("name", "ilike", "lo")]'
        with self.seller_group():
            customers = self.service_with_partner.dispatch("available_customers")
        self.assertEquals(len(customers), 2)
        self.assertEquals(
            {customer["name"] for customer in customers},
            {"Floyd Steward", "Lorraine Douglas"},
        )

        self.backend.seller_access_customer_domain = "[]"
        self.partner.seller_available_customer_domain = '[("name", "ilike", "ou")]'
        with self.seller_group():
            customers = self.service_with_partner.dispatch("available_customers")
        self.assertEquals(len(customers), 4)
        self.assertEquals(
            {customer["name"] for customer in customers},
            {"Douglas Fletcher", "Anonymous", "Lorraine Douglas", "The Jackson Group"},
        )

        self.backend.seller_access_customer_domain = '[("name", "ilike", "lo")]'
        self.partner.seller_available_customer_domain = '[("name", "ilike", "ou")]'
        with self.seller_group():
            customers = self.service_with_partner.dispatch("available_customers")
        self.assertEquals(len(customers), 1)

        self.assertEquals(
            {customer["name"] for customer in customers},
            {"Lorraine Douglas"},
        )
