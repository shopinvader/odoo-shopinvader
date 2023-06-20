# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from functools import partial

from extendable import context
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from requests import Response

from odoo.exceptions import MissingError
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.extendable.registry import _extendable_registries_database
from odoo.addons.fastapi import dependencies
from odoo.addons.fastapi.context import odoo_env_ctx

from ..routers.address_service import address_router
from ..schema import AddressSearch


@tagged("post_install", "-at_install")
class TestShopinvaderAddressApi(TransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        extendable_registry = _extendable_registries_database.get(cls.env.cr.dbname)
        cls.token = context.extendable_registry.set(extendable_registry)
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "FastAPI Shopinvader Address Demo",
                "street": "rue test",
                "zip": "1410",
                "city": "Waterloo",
                "country_id": cls.env.ref("base.be").id,
            }
        )

        test_user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
            }
        )
        test_user.groups_id = [
            (4, cls.env.ref("shopinvader_api_address.shopinvader_addres_user_group").id)
        ]

        cls.app = FastAPI()
        cls.app.include_router(address_router)
        cls.client = TestClient(cls.app)
        cls._ctx_token = odoo_env_ctx.set(cls.env(user=test_user.id))
        cls.app.dependency_overrides[dependencies.authenticated_partner_impl] = partial(
            lambda a: a, cls.test_partner
        )

    @classmethod
    def tearDownClass(cls) -> None:
        odoo_env_ctx.reset(cls._ctx_token)
        context.extendable_registry.reset(cls.token)
        super().tearDownClass()

    def test_create_address(self):
        """
        Test to create a new partner
        """
        data = {
            "name": "test Addr",
            "street": "test Street",
            "zip": "5000",
            "city": "Namur",
            "country": "BEL",
            "type": "other",
        }

        response: Response = self.client.post(
            "/address/create", content=json.dumps(data)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            msg=f"error message: {response.text}",
        )
        response_json = response.json()
        self.assertTrue(response_json)
        self.assertEqual(1, len(response_json["items"]))
        self.assertEqual(1, response_json["total"])

        partner_id = self.env["res.partner"].search([("name", "=", "test Addr")])

        authenticated_partner_id = self.test_partner
        country_belgium_id = self.env["res.country"].search(
            [
                ("code", "=", "BEL"),
            ],
            limit=1,
        )

        self.assertEqual(1, len(partner_id))
        self.assertRecordValues(
            partner_id,
            [
                {
                    "name": "test Addr",
                    "street": "test Street",
                    "zip": "5000",
                    "city": "Namur",
                    "country_id": country_belgium_id.id,
                    "parent_id": authenticated_partner_id.id,
                    "type": "other",
                }
            ],
        )
        self.assertEqual(partner_id, authenticated_partner_id.child_ids)

    def test_get_main_address(self):
        """
        Test to get address of authenticated_partner
        """

        response: Response = self.client.get(
            f"/address/{self.test_partner.id}",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertTrue(response_json)
        self.assertEqual(1, len(response_json["items"]))
        self.assertEqual(1, response_json["total"])
        self.assertEqual(
            response_json["items"][0].get("name"), "FastAPI Shopinvader Address Demo"
        )
        # TODO check fields

    def test_get_new_address(self):
        """
        Test to get address linked to authenticated_partner
        """
        new_address = self.env["res.partner"].create(
            {
                "name": "test New Addr",
                "street": "test Street",
                "zip": "5000",
                "city": "Namur",
                "country_id": self.env.ref("base.be").id,
                "parent_id": self.test_partner.id,
                "type": "other",
            }
        )

        response: Response = self.client.get(
            f"/address/{new_address.id}",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"error message: {response.text}",
        )

        response_json = response.json()
        self.assertTrue(response_json)
        self.assertEqual(1, len(response_json["items"]))
        self.assertEqual(1, response_json["total"])
        self.assertEqual(response_json["items"][0].get("name"), "test New Addr")

    def test_get_address_no_rights(self):
        """
        Try to get address with no rights
        """
        odoo_bot_partner_id = self.env.user.partner_id

        # TODO: change to check http exception
        with self.assertRaises(MissingError):
            response: Response = self.client.get(
                f"/address/{odoo_bot_partner_id.id}",
            )

    # def test_search(self):
    #     """
    #     Search with empty domain
    #     """
    #     response: Response = self.client.post("/address/search", content=json.dumps({}))

    #     self.assertEqual(
    #         response.status_code,
    #         status.HTTP_200_OK,
    #         msg=f"error message: {response.text}",
    #     )
    #     response_json = response.json()
    #     self.assertTrue(response_json)
    #     self.assertEqual(1, len(response_json["items"]))
    #     self.assertEqual(1, response_json["total"])
    #     self.assertEqual(
    #         response_json["items"][0].get("name"), "FastAPI Shopinvader Address Demo"
    #     )

    #     # create one more address
    #     new_address = self.env["res.partner"].create(
    #         {
    #             "name": "test New Addr",
    #             "street": "test Street",
    #             "zip": "5000",
    #             "city": "Namur",
    #             "country_id": self.env.ref("base.be").id,
    #             "parent_id": self.test_partner.id,
    #             "type": "other",
    #         }
    #     )
    #     response: Response = self.client.post("/address/search", content=json.dumps({}))

    #     self.assertEqual(
    #         response.status_code,
    #         status.HTTP_200_OK,
    #         msg=f"error message: {response.text}",
    #     )

    #     # authenticated_partner's address + new_address
    #     response_json = response.json()
    #     self.assertTrue(response_json)
    #     self.assertEqual(2, len(response_json["items"]))
    #     self.assertEqual(2, response_json["total"])

    def test_build_shopinvader_search_address_domain(self):
        data = {
            "name": "test addr search",
            "street": "test street search",
            "street2": "test street2 search",
            "zip": "5000",
            "city": "Namur",
            "phone": "tel123",
            "email": "email",
            "country": "BEL",
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
                "|",
                ("country.name", "ilike", "BEL"),
                ("country.code", "ilike", "BEL"),
            ],
        )
