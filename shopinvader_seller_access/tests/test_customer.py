from odoo.exceptions import AccessDenied

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon

from .common import SellerGroupBackendMixin


class TestCustomer(SellerGroupBackendMixin, TestCustomerCommon):
    def test_get_available_customers(self):
        with self.seller_group():
            customers = self.service_with_partner.dispatch("available_customers")
        self.assertEquals(len(customers), 42)
        self.assertEquals(tuple(customers[0].keys()), ("id", "name", "email"))

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
