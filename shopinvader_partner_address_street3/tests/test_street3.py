# -*- coding: utf-8 -*-
# Copyright 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon


class TestCustomer(TestCustomerCommon):
    @classmethod
    def setUpClass(cls):
        super(TestCustomer, cls).setUpClass()
        cls.data.update({"street3": "rue de l'impasse"})

    def test_create_customer_street3(self):
        self.data["street3"] = ("rue de l'impasse",)
        params = self.data.copy()
        res = self.service.dispatch("create", params=params)["data"]
        partner = self.env["res.partner"].browse(res["id"])
        self._test_partner_data(partner, self.data)
