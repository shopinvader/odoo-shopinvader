import uuid

from odoo.tests.common import tagged

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers.cart import cart_router


@tagged("post_install", "-at_install")
class CommonSaleCart(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "FastAPI Cart Demo"})

        cls.user_no_rights = cls.env["res.users"].create(
            {
                "name": "Test User Without Rights",
                "login": "user_no_rights",
                "groups_id": [(6, 0, [])],
            }
        )
        user_with_rights = cls.env["res.users"].create(
            {
                "name": "Test User With Rights",
                "login": "user_with_rights",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_security_sale.shopinvader_sale_user_group"
                            ).id,
                        ],
                    )
                ],
            }
        )
        cls.default_fastapi_running_user = user_with_rights
        cls.default_fastapi_authenticated_partner = partner.with_user(user_with_rights)
        cls.default_fastapi_router = cart_router

        cls.partner_in_user_no_rights = cls.env(user=cls.user_no_rights)[
            "res.partner"
        ].browse(cls.default_fastapi_authenticated_partner.id)

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "product_2",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.dummy_uuid = str(uuid.uuid4())
        cls.trans_uuid_1 = str(uuid.uuid4())
        cls.trans_uuid_2 = str(uuid.uuid4())
        cls.trans_uuid_3 = str(uuid.uuid4())
        cls.trans_uuid_4 = str(uuid.uuid4())

    def _create_unauthenticated_user_client(self):
        return self._create_test_client(
            user=self.user_no_rights, partner=self.partner_in_user_no_rights
        )
