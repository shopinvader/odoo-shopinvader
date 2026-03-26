# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable import context
from fastapi import status
from requests import Response

from odoo.addons.extendable.registry import _extendable_registries_database
from odoo.addons.fastapi.tests.common import FastAPITransactionCase
from odoo.addons.shopinvader_api_address.routers import address_router


class TestShopinvaderApiAddressShippingNote(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        extendable_registry = _extendable_registries_database.get(cls.env.cr.dbname)
        cls.token = context.extendable_registry.set(extendable_registry)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

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

    @classmethod
    def tearDownClass(cls) -> None:
        context.extendable_registry.reset(cls.token)
        super().tearDownClass()

    def _call_test_client(self, url, http_code=status.HTTP_200_OK, **kwargs):
        method = kwargs.pop("method", "get")
        with self._create_test_client(
            router=self.default_fastapi_router
        ) as test_client:
            response: Response = getattr(test_client, method)(url, **kwargs)
        self.assertEqual(
            response.status_code,
            http_code,
            msg=f"error message: {response.text}",
        )
        return response.json()

    def test_get_shipping_address(self):
        """
        Test to get shipping address of authenticated_partner
        """

        response_json = self._call_test_client("/addresses/delivery")
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

        response_json = self._call_test_client("/addresses/delivery")
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

        response_json = self._call_test_client(
            "/addresses/delivery",
            method="post",
            http_code=status.HTTP_201_CREATED,
            json=data,
        )
        self.assertTrue(response_json)

        address = response_json
        address_id = address.get("id")
        self.assertEqual(address.get("shipping_note"), "test note")

        data = {
            "shipping_note": "new test note",
        }

        address = self._call_test_client(
            f"/addresses/delivery/{address_id}", method="post", json=data
        )
        self.assertEqual(address.get("shipping_note"), "new test note")

        data = {
            "shipping_note": None,
        }

        address = self._call_test_client(
            f"/addresses/delivery/{address_id}", method="post", json=data
        )
        self.assertEqual(address.get("shipping_note"), None)
