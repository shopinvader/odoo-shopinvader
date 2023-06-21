# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from functools import partial

from extendable import context
from fastapi import FastAPI, status
from requests import Response

from odoo.exceptions import MissingError
from odoo.tests.common import tagged
from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from odoo.addons.extendable.registry import _extendable_registries_database
from odoo.addons.fastapi import dependencies
from odoo.addons.fastapi.context import odoo_env_ctx

from ..routers.address_service import address_router
from ..schemas import AddressSearch
from ..routers import address_router


@tagged("post_install", "-at_install")
class TestShopinvaderAddressApi(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        extendable_registry = _extendable_registries_database.get(cls.env.cr.dbname)
        cls.token = context.extendable_registry.set(extendable_registry)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        test_user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
            }
        )
        

        

        cls.test_partner = cls.env["res.partner"].with_user(test_user).create(
            {
                "name": "FastAPI Shopinvader Address Demo",
                "street": "rue test",
                "zip": "1410",
                "city": "Waterloo",
                "country_id": cls.env.ref("base.be").id,
            }
        )
        test_user.groups_id = [
            (6,0, [cls.env.ref("shopinvader_api_address.shopinvader_address_user_group").id])
        ]
        
        cls.default_fastapi_authenticated_partner = (
           cls.test_partner
        )
        cls.default_fastapi_router = address_router



    @classmethod
    def tearDownClass(cls) -> None:
        context.extendable_registry.reset(cls.token)
        super().tearDownClass()

    def test_build_shopinvader_search_address_domain(self):
        data = {
            "name": "test addr search",
            "street": "test street search",
            "street2": "test street2 search",
            "zip": "5000",
            "city": "Namur",
            "phone": "tel123",
            "email": "email",
            "country": self.env.ref("base.be").id,
        }

        addr_search = AddressSearch(**data)

        domain = self.env["res.partner"]._build_shopinvader_search_address_domain(
            addr_search
        )
        self.assertTrue(domain)
        # check equal
        self.assertEqual(
            domain,
            [
                ("name", "ilike", "test addr search"),
                ("street", "ilike", "test addr search"),
                ("street2", "ilike", "test addr search"),
                ("zip", "ilike", "test addr search"),
                ("city", "ilike", "test addr search"),
                ("phone", "ilike", "test addr search"),
                ("email", "ilike", "test addr search"),
                ("country_id", "=",  self.env.ref("base.be").id),
            ],
        )

    def test_get_billing_address(self):
        """
        Test to get address of authenticated_partner
        """
        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                "/addresses/billing",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertTrue(response_json)

        address = response_json

        self.assertEqual(
            address.get("name"), self.test_partner.name
        )
        self.assertEqual(address.get("street"), self.test_partner.street)
        self.assertEqual(address.get("zip"), self.test_partner.zip)
        self.assertEqual(address.get("city"), self.test_partner.city)
        self.assertEqual(address.get("country"), self.test_partner.country_id.id)
        self.assertEqual(address.get("id"), self.test_partner.id)

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
        self.assertTrue(response_json)
        self.assertEqual(0, response_json["total"])

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
        self.assertEqual(1, response_json["total"])

        address = response_json["items"][0]

        self.assertEqual(
            address.get("name"), new_address.name
        )
        self.assertEqual(address.get("street"), new_address.street)
        self.assertEqual(address.get("zip"), new_address.zip)
        self.assertEqual(address.get("city"), new_address.city)
        self.assertEqual(address.get("country"), new_address.country_id.id)
        self.assertEqual(address.get("id"), new_address.id)

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                f"/addresses/shipping/{new_address.id}",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertTrue(response_json)
        self.assertEqual(1, response_json["total"])

        address = response_json["items"][0]

        self.assertEqual(
            address.get("name"), new_address.name
        )
        self.assertEqual(address.get("street"), new_address.street)
        self.assertEqual(address.get("zip"), new_address.zip)
        self.assertEqual(address.get("city"), new_address.city)
        self.assertEqual(address.get("country"), new_address.country_id.id)
        self.assertEqual(address.get("id"), new_address.id)

        #search
        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.get(
                f"/addresses/shipping", params={"zip":"5000"}
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertTrue(response_json)
        self.assertEqual(1, response_json["total"])

        address = response_json["items"][0]

        self.assertEqual(
            address.get("name"), new_address.name
        )
        self.assertEqual(address.get("street"), new_address.street)
        self.assertEqual(address.get("zip"), new_address.zip)
        self.assertEqual(address.get("city"), new_address.city)
        self.assertEqual(address.get("country"), new_address.country_id.id)
        self.assertEqual(address.get("id"), new_address.id)


    def test_create_update_billing_address(self):
        """
        Test to create/update billing address
        """
        data = {
            "street": "test Street",
        }

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.post(
                "/addresses/billing", content=json.dumps(data)
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=f"error message: {response.text}",
        )
        response_json = response.json()
        self.assertTrue(response_json)

        address = response_json

        self.assertEqual(address.get("street"), "test Street")
        self.assertEqual(address.get("street"), self.test_partner.street)

    def test_create_shipping_address(self):
        """
        Test to create shipping address
        """
        data = {
            "name": "test Addr",
            "street": "test Street",
            "zip": "5000",
            "city": "Namur",
            "country": self.env.ref("base.be").id,
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

        self.assertEqual(address.get("street"), "test Street")
        self.assertNotEqual(address.get("street"), self.test_partner.street)

        self.assertEqual(address.get("type"), "delivery")
    
    def test_delete_shipping_address(self):
        """
        Test to delete shipping address
        """

        new_address = self.env["res.partner"].create(
            {
                "name": "test New Addr",
                "street": "test Street",
                "zip": "5000",
                "city": "Namur",
                "country_id": self.env.ref("base.be").id,
                "parent_id": self.test_partner.id,
                "type": "delivery",
            }
        )

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.delete(
                f"/addresses/shipping/{new_address.id}",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        self.assertFalse(new_address.active)

    def test_update_shipping_address(self):
        """
        Test to update shipping address
        """
        new_address = self.env["res.partner"].create(
            {
                "name": "test New Addr",
                "street": "test Street",
                "zip": "5000",
                "city": "Namur",
                "country_id": self.env.ref("base.be").id,
                "parent_id": self.test_partner.id,
                "type": "delivery",
            }
        )

        
        data = {
            "name": "test Addr2",
            "street": "test Street2",
            "zip": "5000",
            "city": "Namur",
        }

        with self._create_test_client(router=address_router) as test_client:
            response: Response = test_client.post(
                f"/addresses/shipping/{new_address.id}", content = json.dumps(data)
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )
        self.assertEqual(new_address.name,data.get("name"))
        self.assertEqual(new_address.street,data.get("street"))