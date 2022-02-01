# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_address import CommonAddressCase


class TestAddress(CommonAddressCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.address_params["siret"] = "00000000000000"

    def _create_address(self, params):
        existing_ids = {
            address["id"] for address in self.address_service.search()["data"]
        }
        res = self.address_service.dispatch("create", params=params)["data"]
        res_ids = {row["id"] for row in res}
        created_ids = res_ids - existing_ids
        return self.env["res.partner"].browse(created_ids)

    def test_create_address(self):
        params = dict(self.address_params, parent_id=self.partner.id)
        address = self._create_address(params)
        self.assertEqual(address.siret, params["siret"])

    def test_update_address(self):
        self.assertFalse(self.address.siret)
        params = dict(siret=self.address_params["siret"], parent_id=self.partner.id)
        self.address_service.dispatch("update", self.address.id, params=params)
        self.assertEqual(self.address.siret, params["siret"])

    def test_read_address(self):
        self.address.siret = "12345678901234"
        params = {"scope": {"id": self.address.id}}
        res = self.address_service.dispatch("search", params=params)["data"][0]
        self.assertEqual(res["siret"], self.address.siret)
