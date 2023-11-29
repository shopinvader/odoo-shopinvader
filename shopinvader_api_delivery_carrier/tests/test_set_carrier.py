# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from requests import Response

from odoo.tests.common import tagged

from odoo.addons.shopinvader_api_cart.routers import cart_router

from .common import TestShopinvaderDeliveryCarrierCommon


@tagged("post_install", "-at_install")
class TestSetCarrier(TestShopinvaderDeliveryCarrierCommon):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_with_rights.groups_id = [
            (
                6,
                0,
                [
                    cls.env.ref(
                        "shopinvader_api_security_sale.shopinvader_sale_user_group"
                    ).id,
                ],
            )
        ]

    def test_setting_free_carrier(self):
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "carrier_id": self.free_carrier.id,
            }
            response: Response = test_client.post(
                "/set_carrier", content=json.dumps(data)
            )
        self.assertEqual(response.status_code, 200)
        info = response.json()
        self.assertEqual(info["delivery"]["amount"]["total"], 0)
        self.assertEqual(
            info["delivery"]["selected_carrier"]["description"],
            self.free_carrier.carrier_description,
        )
        self.assertEqual(
            info["delivery"]["selected_carrier"]["id"], self.free_carrier.id
        )
        self.assertEqual(
            info["delivery"]["selected_carrier"]["name"], self.free_carrier.name
        )
        self.assertEqual(
            info["delivery"]["selected_carrier"]["code"], self.free_carrier.code
        )

    def test_setting_poste_carrier(self):
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "carrier_id": self.poste_carrier.id,
            }
            response: Response = test_client.post(
                "/set_carrier", content=json.dumps(data)
            )
        self.assertEqual(response.status_code, 200)
        info = response.json()
        # Check delivery amount
        self.assertEqual(info["delivery"]["amount"]["total"], 24)
        self.assertEqual(info["delivery"]["amount"]["untaxed"], 20)
        self.assertEqual(info["delivery"]["amount"]["tax"], 4)

        # Check total amount
        self.assertEqual(info["amount"]["total"], 750 + 24)
        self.assertEqual(info["amount"]["untaxed"], 750 + 20)
        self.assertEqual(info["amount"]["tax"], 4)

        # Check total without shipping prices
        total_without_shipping = (
            info["amount"]["total"] - info["delivery"]["amount"]["total"]
        )
        self.assertEqual(
            info["amount"]["total_without_shipping"], total_without_shipping
        )
        untaxed_without_shipping = (
            info["amount"]["untaxed"] - info["delivery"]["amount"]["untaxed"]
        )
        self.assertEqual(
            info["amount"]["untaxed_without_shipping"], untaxed_without_shipping
        )
        tax_without_shipping = info["amount"]["tax"] - info["delivery"]["amount"]["tax"]
        self.assertEqual(info["amount"]["tax_without_shipping"], tax_without_shipping)

        # Check selected carrier
        self.assertEqual(
            info["delivery"]["selected_carrier"]["description"],
            self.poste_carrier.carrier_description,
        )
        self.assertEqual(
            info["delivery"]["selected_carrier"]["id"], self.poste_carrier.id
        )
        self.assertEqual(
            info["delivery"]["selected_carrier"]["name"], self.poste_carrier.name
        )
        self.assertEqual(
            info["delivery"]["selected_carrier"]["code"], self.poste_carrier.code
        )
