# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon


class TestCustomer(TestCustomerCommon):
    def test_create_customer_validation_none(self):
        data = dict(self.data, external_id="12345678", email="acme@foo.com")
        # validation is not active
        self.assertFalse(self.backend.validate_customers)
        res = self.service.dispatch("create", params=data)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        # hence is enabled by default
        self.assertTrue(partner.is_shopinvader_active)
        # enable validation for all
        self.backend.update(
            dict(validate_customers=True, validate_customers_type="all")
        )
        # and create a new one
        data = dict(self.data, external_id="D5CdkqOEL", email="funny@foo.com")
        self.service._reset_partner_work_context()
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
            self.env,
            name="Just A User",
            email="just@auser.com",
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
