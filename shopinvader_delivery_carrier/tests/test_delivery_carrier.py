# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import CommonCarrierCase


class TestDeliveryCarrier(CommonCarrierCase):
    def setUp(self):
        super(TestDeliveryCarrier, self).setUp()
        self.carrier_service = self.service.component("delivery_carriers")

    def _check_response(self, res, expected):
        expected.update({"count": expected["size"], "rows": expected["data"]})
        self.assertDictEqual(res, expected)

    def test_search_all(self):
        res = self.carrier_service.search()
        expected = {
            "size": 2,
            "data": [
                {
                    "price": 0.0,
                    "description": self.free_carrier.description or None,
                    "id": self.free_carrier.id,
                    "name": self.free_carrier.name,
                    "code": self.free_carrier.code,
                    "type": None,
                },
                {
                    "price": 0.0,
                    "description": self.poste_carrier.description or None,
                    "id": self.poste_carrier.id,
                    "name": self.poste_carrier.name,
                    "code": self.poste_carrier.code,
                    "type": None,
                },
            ],
        }
        self._check_response(res, expected)

    def test_search_current_cart(self):
        res = self.carrier_service.search(target="current_cart")
        expected = {
            "size": 2,
            "data": [
                {
                    "price": 0.0,
                    "description": self.free_carrier.description or None,
                    "id": self.free_carrier.id,
                    "name": self.free_carrier.name,
                    "code": self.free_carrier.code,
                    "type": None,
                },
                {
                    "price": 20.0,
                    "description": self.poste_carrier.description or None,
                    "id": self.poste_carrier.id,
                    "name": self.poste_carrier.name,
                    "code": self.poste_carrier.code,
                    "type": None,
                },
            ],
        }
        self._check_response(res, expected)


class DeprecatedTestDeliveryCarrier(TestDeliveryCarrier):
    def setUp(self):
        super(DeprecatedTestDeliveryCarrier, self).setUp()
        self.carrier_service = self.service.component("delivery_carrier")
