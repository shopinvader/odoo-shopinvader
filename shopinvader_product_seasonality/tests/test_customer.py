# Copyright 2021 Camptocamp SA (http://www.camptocamp.com).
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_customer import TestCustomerCommon


class TestCustomer(TestCustomerCommon):
    def test_customer_info(self):
        self.data["external_id"] = "qOELD5Cdk"
        self.service.dispatch("create", params=self.data)["data"]
        seasonal_conf = self.env["seasonal.config"].create(
            {"name": "Test seasonal conf shop"}
        )
        self.service.partner.seasonal_config_id = seasonal_conf
        res = self.service.dispatch("get")
        self.assertEqual(res["data"]["seasonal_config_id"], seasonal_conf.id)
