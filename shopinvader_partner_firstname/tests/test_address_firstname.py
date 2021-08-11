# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_address import CommonAddressCase


class TestAddressFirstName(CommonAddressCase):
    def test_create_address_firstname(self):
        params = self.address_params.copy()
        params.pop("name")
        params["lastname"] = "last"
        params["firstname"] = "first"
        data = self.address_service.dispatch("create", params=params)["data"]
        address = self.env["res.partner"].browse(data[-1]["id"])
        self.assertEqual(address.parent_id, self.partner)
        self.check_data(address, params)
