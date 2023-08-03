# Copyright 2021 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_v1_base.tests.test_address import CommonAddressCase


class TestAddress(CommonAddressCase):
    def test_address_create(self):
        params = self.address_params.copy()
        params.update(
            {
                "partner_invoice_id": self.address.id,
                "partner_delivery_id": self.address_2.id,
            }
        )
        self.address_service.dispatch("create", params=params)["data"]
        partner = self.env["res.partner"].search([("name", "=", params["name"])])
        self.assertEqual(partner.partner_invoice_id, self.address)
        self.assertEqual(partner.partner_delivery_id, self.address_2)

    def test_address_update(self):
        params = {
            "partner_invoice_id": self.address.id,
            "partner_delivery_id": self.address_2.id,
        }
        self.address_service.dispatch("update", self.partner.id, params=params)["data"]
        self.assertEqual(self.partner.partner_invoice_id, self.address)
        self.assertEqual(self.partner.partner_delivery_id, self.address_2)

    def test_address_update_clear(self):
        self.partner.partner_invoice_id = self.address
        self.partner.partner_delivery_id = self.address_2
        params = {
            "partner_invoice_id": False,
            "partner_delivery_id": False,
        }
        self.address_service.dispatch("update", self.partner.id, params=params)["data"]
        self.assertFalse(self.partner.partner_invoice_id)
        self.assertFalse(self.partner.partner_delivery_id)

    def test_address_read(self):
        self.partner.partner_invoice_id = self.address
        self.partner.partner_delivery_id = self.address_2
        data = self.address_service.dispatch("get", self.partner.id)[0]
        self.assertEqual(data["partner_invoice_id"]["id"], self.address.id)
        self.assertEqual(data["partner_delivery_id"]["id"], self.address_2.id)
