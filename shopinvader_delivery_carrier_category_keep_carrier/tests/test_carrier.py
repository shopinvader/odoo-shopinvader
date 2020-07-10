# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_delivery_carrier.tests.common import (
    CommonCarrierCase,
)


class CarrierCase(CommonCarrierCase):
    @classmethod
    def setUpClass(cls):
        super(CarrierCase, cls).setUpClass()
        cls.category_dropoff = cls.env.ref(
            "delivery_carrier_category.delivery_carrier_category_dropoff"
        )
        cls.poste_carrier.category_id = cls.category_dropoff
        cls.category_dropoff.keep_carrier_on_shipping_change = True

    def test_reset_carrier_on_changing_delivery_address_keep(self):
        # Set the delivery carrier category to keep it
        self._apply_carrier_and_assert_set()
        cart = self.service.dispatch(
            "update", params={"shipping": {"address": {"id": self.address.id}}}
        )["data"]
        self.assertEqual(cart["shipping"]["amount"]["total"], 20.0)
        self.assertEquals(
            self.poste_carrier.code,
            cart["shipping"]["selected_carrier"]["code"],
        )
