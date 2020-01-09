# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon


class TestCustomer(TestCustomerCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_create_customer_firstname(self):
        data = dict(
            self.data,
            external_id="jdoe",
            email="john@doe.com",
            firstname="John",
            lastname="Doe",
        )
        params = data.copy()
        res = self.service.dispatch("create", params=params)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        data["name"] = "John Doe"
        self._test_partner_data(partner, data)
