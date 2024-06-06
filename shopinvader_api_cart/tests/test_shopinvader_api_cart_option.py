# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import random

from odoo_test_helper import FakeModelLoader

from odoo.addons.shopinvader_schema_sale.schemas import sale_line_option

from ..routers.cart import cart_router
from .common import CommonSaleCart

NUMBER = range(1, 3)


class SaleLineOption(sale_line_option.SaleLineOption, extends=True):
    note: str | None = None

    @classmethod
    def _prepare_from_sale_order_line(cls, line):
        vals = super()._prepare_from_sale_order_line(line)
        if hasattr(line, "note") and line.note:
            vals["note"] = line.note
        return vals


class TestSaleCartOption(CommonSaleCart):
    @classmethod
    def setUpClass(cls):
        super(TestSaleCartOption, cls).setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_model import SaleOrderLine, ShopinvaderApiCartRouterHelper

        cls.loader.update_registry((SaleOrderLine,))
        # cls.loader.update_registry((SaleOrderLine, ShopinvaderApiCartRouterHelper))
        cls.loader.update_registry((ShopinvaderApiCartRouterHelper,))

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super(TestSaleCartOption, cls).tearDownClass()

    def test_transactions(self) -> None:
        so = self.env["sale.order"]._create_empty_cart(
            self.default_fastapi_authenticated_partner.id
        )
        data = {
            "transactions": [
                {
                    "uuid": self.trans_uuid_1,
                    "product_id": self.product_1.id,
                    "qty": 1,
                    "options": {"note": str(random.Random(NUMBER))},
                }
            ]
        }
        with self._create_test_client(router=cart_router) as test_client:
            test_client.post(f"/{so.uuid}/sync", content=json.dumps(data))
        line = so.order_line
        self.assertEqual(1, line.product_uom_qty)
        self.assertIn(line.note, ("1", "2"), "Note field should be 1 or 2")
