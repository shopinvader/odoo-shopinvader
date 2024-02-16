# Copyright 2021 David BEAL @ Akretion
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.exceptions import UserError

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon


class TestCustomer(TestCustomerCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # TODO: This should be in setUpClass, but it should be changed
        # in shopinvader TestCustomerCommon
        self.data["street3"] = "Bâtiment A"

    def test_create_customer_street3(self):
        self.data["street3"] = "Bâtiment A"
        params = self.data.copy()
        res = self.service.dispatch("create", params=params)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        self._test_partner_data(partner, self.data)

    def test_create_customer_street3_bad_type(self):
        self.data["street3"] = 42
        params = self.data.copy()
        with self.assertRaises(UserError):
            self.service.dispatch("create", params=params)
