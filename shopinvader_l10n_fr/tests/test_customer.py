# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon


class TestCustomer(TestCustomerCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.data["siret"] = "00000000000000"

    def test_create_customer(self):
        params = dict(self.data, external_id="D5CdkqOEL")
        res = self.service.dispatch("create", params=params)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        self.assertEqual(partner.siret, params["siret"])

    def test_update_customer(self):
        params = {"siret": self.data["siret"]}
        self.service_with_partner.dispatch("update", self.partner.id, params=params)
        self.assertEqual(self.partner.siret, params["siret"])
