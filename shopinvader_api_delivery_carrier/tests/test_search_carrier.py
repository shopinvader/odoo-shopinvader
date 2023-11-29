# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from requests import Response

from odoo.tests.common import tagged

from ..routers import delivery_carrier_router
from .common import TestShopinvaderDeliveryCarrierCommon


@tagged("post_install", "-at_install")
class TestSetCarrier(TestShopinvaderDeliveryCarrierCommon):
    def test_search_all(self):
        with self._create_test_client(router=delivery_carrier_router) as test_client:
            response: Response = test_client.get("/delivery_carriers", params={})

        self.assertEqual(response.status_code, 200)
        info = response.json()
        expected = [
            {
                "description": self.free_carrier.carrier_description or None,
                "id": self.free_carrier.id,
                "name": self.free_carrier.name,
                "code": self.free_carrier.code or None,
            },
            {
                "description": self.poste_carrier.carrier_description or None,
                "id": self.poste_carrier.id,
                "name": self.poste_carrier.name,
                "code": self.poste_carrier.code or None,
            },
            {
                "description": self.local_carrier.carrier_description or None,
                "id": self.local_carrier.id,
                "name": self.local_carrier.name,
                "code": self.local_carrier.code or None,
            },
        ]
        self.assertEqual(info, expected)

    def test_search_current_cart(self):
        """
        Test that the right structure is returned when searching for delivery
        carriers that can be applied to current cart.
        :return:
        """
        with self._create_test_client(router=delivery_carrier_router) as test_client:
            response: Response = test_client.get(
                "/current/delivery_carriers", params={}
            )
        self.assertEqual(response.status_code, 200)
        info = response.json()
        expected = [
            {
                "price_applied_to_cart": 0.0,
                "description": self.free_carrier.carrier_description or None,
                "id": self.free_carrier.id,
                "name": self.free_carrier.name,
                "code": self.free_carrier.code or None,
            },
            {
                "price_applied_to_cart": 0.0,
                "description": self.local_carrier.carrier_description or None,
                "id": self.local_carrier.id,
                "name": self.local_carrier.name,
                "code": self.local_carrier.code or None,
            },
            {
                "price_applied_to_cart": 20.0,
                "description": self.poste_carrier.carrier_description or None,
                "id": self.poste_carrier.id,
                "name": self.poste_carrier.name,
                "code": self.poste_carrier.code or None,
            },
        ]
        self.assertEqual(info, expected)

    def test_search_current_cart_with_uuid(self):
        """
        Same test as above, but with the route specifying the cart UUID:

        Test that the right structure is returned when searching for delivery
        carriers that can be applied to current cart.
        """
        with self._create_test_client(router=delivery_carrier_router) as test_client:
            response: Response = test_client.get(
                f"/{self.cart.uuid}/delivery_carriers", params={}
            )
        self.assertEqual(response.status_code, 200)
        info = response.json()
        expected = [
            {
                "price_applied_to_cart": 0.0,
                "description": self.free_carrier.carrier_description or None,
                "id": self.free_carrier.id,
                "name": self.free_carrier.name,
                "code": self.free_carrier.code or None,
            },
            {
                "price_applied_to_cart": 0.0,
                "description": self.local_carrier.carrier_description or None,
                "id": self.local_carrier.id,
                "name": self.local_carrier.name,
                "code": self.local_carrier.code or None,
            },
            {
                "price_applied_to_cart": 20.0,
                "description": self.poste_carrier.carrier_description or None,
                "id": self.poste_carrier.id,
                "name": self.poste_carrier.name,
                "code": self.poste_carrier.code or None,
            },
        ]
        self.assertEqual(info, expected)

    def test_search_current_cart_no_cart(self):
        """
        Delete the current cart and try to search on delivery carriers
        for the current cart -> Raise HTTPException
        """
        self.cart.sudo().unlink()
        with self._create_test_client(router=delivery_carrier_router) as test_client:
            response: Response = test_client.get(
                "/current/delivery_carriers", params={}
            )
        self.assertEqual(response.status_code, 404)

    def test_search_current_cart_country(self):
        partner_country = self.cart.partner_id.country_id
        self.poste_carrier.country_ids = self.env.ref("base.be")
        self.local_carrier.country_ids = self.env.ref("base.be")
        with self._create_test_client(router=delivery_carrier_router) as test_client:
            response: Response = test_client.get(
                "/current/delivery_carriers",
                params={"country_id": self.env.ref("base.us").id},
            )
        self.assertEqual(response.status_code, 200)
        info = response.json()
        expected = [
            {
                "price_applied_to_cart": 0.0,
                "description": self.free_carrier.carrier_description or None,
                "id": self.free_carrier.id,
                "name": self.free_carrier.name,
                "code": self.free_carrier.code or None,
            }
        ]
        self.assertEqual(info, expected)
        # Check if partner country hasn't been modified
        self.assertEqual(partner_country, self.cart.partner_id.country_id)

    def test_search_current_cart_no_zip(self):
        # Limit carriers to countries, 2 to BE, one to FR
        # First limit FR carrier zips with 750 prefix, test on 75100
        # No carrier should be available
        partner_zip = self.cart.partner_id.zip
        self.free_carrier.country_ids = self.env.ref("base.be")
        self.local_carrier.country_ids = self.env.ref("base.be")
        self.poste_carrier.country_ids = self.env.ref("base.fr")
        self.poste_carrier.zip_prefix_ids = [(0, 0, {"name": "750"})]
        with self._create_test_client(router=delivery_carrier_router) as test_client:
            data = {
                "zipcode": "75100",
                "country_id": self.env.ref("base.fr").id,
            }
            response: Response = test_client.get(
                "/current/delivery_carriers", params=data
            )
        self.assertEqual(response.status_code, 200)
        info = response.json()
        expected = []
        self.assertEqual(info, expected)
        # Check if partner zip hasn't been modified
        self.assertEqual(partner_zip, self.cart.partner_id.zip)

    def test_search_current_cart_zip(self):
        # Limit both carriers to countries, one to BE, one to FR
        # Change carrier zips to allows zips from 75000 to 75200
        partner_zip = self.cart.partner_id.zip
        self.free_carrier.country_ids = self.env.ref("base.be")
        self.local_carrier.country_ids = self.env.ref("base.be")
        self.poste_carrier.country_ids = self.env.ref("base.fr")

        # Change carrier zips
        self.poste_carrier.zip_prefix_ids = [
            (0, 0, {"name": "750"}),
            (0, 0, {"name": "751"}),
            (0, 0, {"name": "752"}),
        ]

        with self._create_test_client(router=delivery_carrier_router) as test_client:
            data = {
                "zipcode": "75100",
                "country_id": self.env.ref("base.fr").id,
            }
            response: Response = test_client.get(
                "/current/delivery_carriers", params=data
            )
        self.assertEqual(response.status_code, 200)
        info = response.json()
        expected = [
            {
                "description": self.poste_carrier.carrier_description or None,
                "id": self.poste_carrier.id,
                "name": self.poste_carrier.name,
                "code": self.poste_carrier.code or None,
                "price_applied_to_cart": 20.0,
            }
        ]
        self.assertEqual(info, expected)
        # Check if partner zip hasn't been modified
        self.assertEqual(partner_zip, self.cart.partner_id.zip)
