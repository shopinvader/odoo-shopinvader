# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tools import mute_logger

from .common import CommonCase
from .test_address import _check_partner_data

_logger = logging.getLogger(__name__)


class TestCustomerCommon(CommonCase):
    def setUp(self, *args, **kwargs):
        super(TestCustomerCommon, self).setUp(*args, **kwargs)
        self.data = {
            "email": "new@customer.example.com",
            "name": "Purple",
            "street": "Rue du jardin",
            "zip": "43110",
            "city": "Aurec sur Loire",
            "phone": "0485485454",
            "country": {"id": self.env.ref("base.fr").id},
            "is_company": False,
        }
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="customer")
            self.address_service = work.component(usage="addresses")

    def _test_partner_data(self, partner, data):
        _check_partner_data(self, partner, data)


class TestCustomer(TestCustomerCommon):
    def test_create_customer(self):
        self.data["external_id"] = "D5CdkqOEL"
        res = self.service.dispatch("create", params=self.data)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        self._test_partner_data(partner, self.data)

    def test_create_customer_business_vat_only(self):
        self.data["external_id"] = "D5CdkqOEL"
        # no `is_company` flag
        self.data["vat"] = "BE0477472701"
        res = self.service.dispatch("create", params=self.data)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        # no flag, no company, no party :)
        self.assertEqual(partner.is_company, False)

    def test_create_customer_business(self):
        self.data["external_id"] = "D5CdkqOEL"
        self.data["is_company"] = True
        self.data["vat"] = "BE0477472701"
        res = self.service.dispatch("create", params=self.data)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        self.assertEqual(partner.is_company, True)

    def test_address_type(self):
        partner = self.env.ref("shopinvader.partner_1")
        self.assertEqual(partner.address_type, "profile")
        address = self.env.ref("shopinvader.partner_1_address_1")
        self.assertEqual(address.address_type, "address")

    def test_update_address_type(self):
        data = {"email": "address@customer.example.com", "name": "Address"}
        partner = self.env["res.partner"].create(data)
        self.assertEqual(partner.address_type, "profile")
        data = {"email": "parent@customer.example.com", "name": "Parent"}
        parent = self.env["res.partner"].create(data)
        partner.parent_id = parent.id
        self.assertEqual(partner.address_type, "address")

    def test_create_no_create_cart(self):
        """
        Create a customer should not create an empty cart
        """
        self.data["external_id"] = "D5CdkqOEL"
        res = self.service.dispatch("create", params=self.data)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        sale_domain = [("partner_id", "=", partner.id)]
        SaleOrder = self.env["sale.order"]
        self.assertFalse(SaleOrder.search(sale_domain))

    @mute_logger("odoo.models.unlink")
    def test_sign_in_no_create_cart(self):
        """
        Customer sign-in should not create an empty cart
        """
        partner = self.env.ref("shopinvader.partner_1")
        sale_domain = [("partner_id", "=", partner.id)]
        SaleOrder = self.env["sale.order"]
        SaleOrder.search(sale_domain).unlink()

        invader_partner = partner._get_invader_partner(self.backend)
        self.service._load_partner_work_context(invader_partner)
        self.service.sign_in()
        self.assertFalse(SaleOrder.search(sale_domain))

    def test_create_customer_validation_none(self):
        data = dict(self.data, external_id="12345678", email="acme@foo.com")
        # validation is not active
        self.assertFalse(self.backend.validate_customers)
        res = self.service.dispatch("create", params=data)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        # hence is enabled by default
        self.assertTrue(partner.is_shopinvader_active)

    def test_create_customer_validation_all(self):
        # enable validation for all
        self.backend.update(
            dict(validate_customers=True, validate_customers_type="all")
        )
        data = dict(self.data, external_id="D5CdkqOEL", email="funny@foo.com")
        res = self.service.dispatch("create", params=data)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        invader_partner = partner._get_invader_partner(self.backend)
        # must not be validated
        self.assertFalse(invader_partner.is_shopinvader_active)
        self.assertTrue(partner.has_shopinvader_user_to_validate)
        # now let's enable it w/ specific action
        invader_partner._get_shopinvader_validate_wizard().action_apply()
        self.assertTrue(invader_partner.is_shopinvader_active)
        self.assertFalse(partner.has_shopinvader_user_to_validate)
        # no let's call an update -> validation state won't change
        data = dict(data, email="funny@boo.com")
        self.address_service.dispatch("update", partner.id, params=data)
        self.assertFalse(partner.has_shopinvader_user_to_validate)

    def test_create_customer_validation_company_user_enabled(self):
        data = dict(
            self.data,
            external_id="12345678X",
            is_company=True,
            vat="BE0477472701",
            email="acme@foo.com",
        )
        # validation is active but only for simple users
        self.backend.update(
            dict(validate_customers=True, validate_customers_type="user")
        )
        res = self.service.dispatch("create", params=data)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        # hence the company is enabled
        self.assertTrue(partner.is_shopinvader_active)

    def test_create_customer_validation_company_company_enabled(self):
        # now enable it for company only
        self.backend.update(
            dict(validate_customers=True, validate_customers_type="company")
        )
        data = dict(
            self.data,
            external_id="12345678Y",
            is_company=True,
            vat="BE0477472701",
            email="company@foo.com",
        )
        res = self.service.dispatch("create", params=data)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        invader_partner = partner._get_invader_partner(self.backend)
        self.assertFalse(invader_partner.is_shopinvader_active)
        self.assertTrue(partner.has_shopinvader_user_to_validate)
        # now let's enable it w/ specific action
        invader_partner._get_shopinvader_validate_wizard().action_apply()
        self.assertTrue(invader_partner.is_shopinvader_active)
        self.assertFalse(partner.has_shopinvader_user_to_validate)

    def test_has_address_to_validate(self):
        invader_partner = self._create_invader_partner(
            self.env, name="Just A User", email="just@auser.com",
        )
        self.assertTrue(invader_partner.is_shopinvader_active)
        partner = invader_partner.record_id
        self.assertTrue(partner.has_shopinvader_user)
        self.assertFalse(partner.has_shopinvader_user_to_validate)
        self.assertFalse(partner.has_shopinvader_address_to_validate)
        addr1 = partner.create(
            {
                "address_type": "address",
                "parent_id": partner.id,
                "name": "Just a contact",
            }
        )
        self.assertFalse(addr1.is_shopinvader_active)
        self.assertTrue(partner.has_shopinvader_address_to_validate)
