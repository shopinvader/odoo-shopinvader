# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon


class TestCustomer(TestCustomerCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # TODO: Move to setUpClass in shopinvader's TestCustomerCommon.
        self.data["invoicing_mode"] = "standard"

    def test_create_customer(self):
        self.data["external_id"] = "D5CdkqOEL"
        res = self.service.dispatch("create", params=self.data)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        self._test_partner_data(partner, self.data)
