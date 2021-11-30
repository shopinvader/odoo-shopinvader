# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.exceptions import MissingError, UserError
from odoo.tools import mute_logger

from .common import CommonCase
from .test_address import _check_partner_data

_logger = logging.getLogger(__name__)


class TestCustomerCommon(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestCustomerCommon, cls).setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.partner_binding = cls.env.ref("shopinvader.shopinvader_partner_1")
        cls.address = cls.env.ref("shopinvader.partner_1_address_1")
        cls.partner_2 = cls.env.ref("shopinvader.partner_2")

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

        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service_with_partner = work.component(usage="customer")

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

    def test_update_customer(self):
        params = {"street": "New Street"}
        res = self.service_with_partner.dispatch(
            "update", self.partner.id, params=params
        )
        self.assertEqual(res["data"]["id"], self.partner.id)
        self.assertEquals(self.partner.street, "New Street")
        self.assertEquals(self.partner_binding.street, "New Street")

    def test_update_customer_no_partner(self):
        params = {"street": "New Street"}
        with self.assertRaises(UserError):
            self.service.dispatch("update", self.partner.id, params=params)

    def test_update_customer_binding(self):
        params = {"external_id": "D5CdkqOEL"}
        res = self.service_with_partner.dispatch(
            "update", self.partner.id, params=params
        )
        self.assertEqual(res["data"]["id"], self.partner.id)
        self.assertEquals(self.partner_binding.external_id, "D5CdkqOEL")

    def test_update_customer_not_allowed(self):
        params = {"street": "New Street"}

        with self.assertRaises(MissingError):
            self.service_with_partner.dispatch(
                "update", self.partner_2.id, params=params
            )

    def test_update_customer_child_not_allowed(self):
        params = {"street": "New Street"}
        with self.assertRaises(UserError):
            self.service_with_partner.dispatch("update", self.address.id, params=params)
