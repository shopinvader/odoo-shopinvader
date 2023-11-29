# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2023 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import uuid

from odoo.tests.common import new_test_user

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.shopinvader_api_cart.routers import cart_router


class TestShopinvaderDeliveryCarrierCommon(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {"name": "FastAPI Delivery Carrier Demo"}
        )
        cls.user_with_rights = new_test_user(
            cls.env,
            login="user_with_rights",
            groups="shopinvader_api_delivery_carrier.shopinvader_delivery_carrier_user_group",
        )
        cls.default_fastapi_running_user = cls.user_with_rights
        cls.default_fastapi_authenticated_partner = cls.partner.with_user(
            cls.user_with_rights
        )
        cls.default_fastapi_router = cart_router

        cls.tax_20 = cls.env["account.tax"].create(
            {
                "name": "Tax 20%",
                "amount": 20,
            }
        )

        cls.free_carrier = cls.env.ref("delivery.free_delivery_carrier")
        cls.poste_carrier = cls.env.ref("delivery.delivery_carrier")
        cls.local_carrier = cls.env.ref("delivery.delivery_local_delivery")
        cls.free_carrier.code = "FREE"
        cls.free_carrier.carrier_description = "delivery in 5 days"
        cls.poste_carrier.code = "POSTE"
        cls.poste_carrier.carrier_description = "delivery in 2 days"
        cls.poste_carrier.product_id.taxes_id = [(6, 0, [cls.tax_20.id])]
        cls.product_1 = cls.env.ref("product.product_product_4b")
        cls.precision = 2

        cls.cart = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "typology": "cart",
                "uuid": str(uuid.uuid4()),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_1.id,
                        },
                    )
                ],
            }
        )
