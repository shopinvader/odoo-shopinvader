# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import CommonCarrierCase


class TestDeliveryCarrier(CommonCarrierCase):
    def setUp(self):
        super(CommonCarrierCase, self).setUp()
        self.carrier_service = self.service.component("delivery_carrier")

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
                    "description": self.free_carrier.description,
                    "id": self.free_carrier.id,
                    "name": self.free_carrier.name,
                    "code": self.free_carrier.code,
                    "type": None,
                },
                {
                    "price": 0.0,
                    "description": self.poste_carrier.description,
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
                    "description": self.free_carrier.description,
                    "id": self.free_carrier.id,
                    "name": self.free_carrier.name,
                    "code": self.free_carrier.code,
                    "type": None,
                },
                {
                    "price": 20.0,
                    "description": self.poste_carrier.description,
                    "id": self.poste_carrier.id,
                    "name": self.poste_carrier.name,
                    "code": self.poste_carrier.code,
                    "type": None,
                },
            ],
        }
        self._check_response(res, expected)

    def test_search_current_cart_country(self):
        partner_country = self.cart.partner_id.country_id
        self.poste_carrier.country_ids = self.env.ref("base.be")
        self.params = {
            "target": "current_cart",
            "country_id": self.env.ref("base.us").id,
        }
        res = self.carrier_service.dispatch("search", params=self.params)
        expected = {
            "size": 1,
            "data": [
                {
                    "price": 0.0,
                    "description": self.free_carrier.description,
                    "id": self.free_carrier.id,
                    "name": self.free_carrier.name,
                    "code": self.free_carrier.code,
                    "type": None,
                }
            ],
        }
        self._check_response(res, expected)
        # Check if partner country hasn't been modified
        self.assertEquals(partner_country, self.cart.partner_id.country_id)

    def test_search_current_cart_no_zip(self):
        # Limit both carriers to countries, one to BE, one to FR
        # First limit FR carrier to 75000 zip, test on 75100
        # No carrier should be available
        partner_zip = self.cart.partner_id.zip
        self.free_carrier.country_ids = self.env.ref("base.be")
        self.poste_carrier.country_ids = self.env.ref("base.fr")
        self.poste_carrier.zip_from = "75000"
        self.poste_carrier.zip_to = "75000"
        self.params = {
            "target": "current_cart",
            "zip_code": "75100",
            "country_id": self.env.ref("base.fr").id,
        }
        res = self.carrier_service.dispatch("search", params=self.params)
        expected = {"size": 0, "data": []}
        self._check_response(res, expected)
        # Check if partner zip hasn't been modified
        self.assertEquals(partner_zip, self.cart.partner_id.zip)

    def test_search_current_cart_zip(self):
        # Limit both carriers to countries, one to BE, one to FR
        # Change carrier zips to 75000 > 75200
        self.free_carrier.country_ids = self.env.ref("base.be")
        self.poste_carrier.country_ids = self.env.ref("base.fr")

        # Change carrier zips
        self.poste_carrier.zip_from = "75000"
        self.poste_carrier.zip_to = "75200"
        self.params = {
            "target": "current_cart",
            "zip_code": "75100",
            "country_id": self.env.ref("base.fr").id,
        }
        res = self.carrier_service.dispatch("search", params=self.params)
        expected = {
            "size": 1,
            "data": [
                {
                    "price": 0.0,
                    "description": self.poste_carrier.description,
                    "id": self.poste_carrier.id,
                    "name": self.poste_carrier.name,
                    "code": self.poste_carrier.code,
                    "type": None,
                }
            ],
        }
        self._check_response(res, expected)
