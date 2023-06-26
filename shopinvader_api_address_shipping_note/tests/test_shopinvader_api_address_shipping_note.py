# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.shopinvader_api_address.routers import address_router


@tagged("post_install", "-at_install")
class TestShopinvaderApiAddressShippingNote(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_address.shopinvader_address_user_group"
                            ).id
                        ],
                    )
                ],
            }
        )

        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "FastAPI Shopinvader Address Demo",
                "street": "rue test",
                "zip": "1410",
                "city": "Waterloo",
                "country_id": cls.env.ref("base.be").id,
            }
        )

        cls.default_fastapi_authenticated_partner = cls.test_partner
        cls.default_fastapi_router = address_router

    def test_get_shipping_address(self):
        """
        Test to get shipping address of authenticated_partner
        """

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                "/addresses/shipping",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertEqual(0, len(response_json))

        # add shipping address
        new_address = self.env["res.partner"].create(
            {
                "name": "test New Addr",
                "street": "test Street",
                "zip": "5000",
                "city": "Namur",
                "country_id": self.env.ref("base.be").id,
                "parent_id": self.test_partner.id,
                "type": "delivery",
                "shipping_note": "test note",
            }
        )

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                "/addresses/shipping",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertTrue(response_json)

        address = response_json[0]

        self.assertEqual(address.get("name"), new_address.name)
        self.assertEqual(address.get("street"), new_address.street)
        self.assertEqual(address.get("zip"), new_address.zip)
        self.assertEqual(address.get("city"), new_address.city)
        self.assertEqual(address.get("country_id"), new_address.country_id.id)
        self.assertEqual(address.get("id"), new_address.id)
        self.assertEqual(address.get("shipping_note"), new_address.shipping_note)

    def test_create_shipping_address(self):
        """
        Test to create shipping address
        """
        data = {
            "name": "test Addr",
            "street": "test Street",
            "zip": "5000",
            "city": "Namur",
            "country_id": self.env.ref("base.be").id,
            "shipping_note": "test note",
        }

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.post(
                "/addresses/shipping", content=json.dumps(data)
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=f"error message: {response.text}",
        )
        response_json = response.json()
        self.assertTrue(response_json)

        address = response_json

        self.assertEqual(address.get("shipping_note"), "test note")
