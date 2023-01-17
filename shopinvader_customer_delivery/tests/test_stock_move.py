from odoo.exceptions import AccessDenied

from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.addons.shopinvader_seller_access.tests.common import SellerGroupBackendMixin


class TestStockMove(SellerGroupBackendMixin, CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.partner_2 = cls.env.ref("shopinvader.partner_2")
        cls.user_of_partner_2 = cls.env["res.users"].create(
            {
                "login": "partner_2",
                "partner_id": cls.partner_2.id,
            }
        )
        cls.productA = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "default_code": "PRODUCT_A",
            }
        )
        cls.productB = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "default_code": "PRODUCT_B",
            }
        )
        cls.productC = cls.env["product.product"].create(
            {
                "name": "Product C",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "default_code": "PRODUCT_C",
            }
        )

        cls.env["stock.quant"].create(
            {
                "product_id": cls.productA.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 30.0,
            }
        )

        cls.env["stock.quant"].create(
            {
                "product_id": cls.productB.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 10.0,
            }
        )

        cls.env["stock.quant"].create(
            {
                "product_id": cls.productC.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 100.0,
            }
        )

        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": (i + 1) * 10,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                    for i, p in enumerate([cls.productA, cls.productB])
                ],
                "picking_policy": "direct",
                "shopinvader_backend_id": cls.backend.id,
            }
        )

        cls.so2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "user_id": cls.user_of_partner_2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": (2 - i) * 7,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                    for i, p in enumerate([cls.productA, cls.productC])
                ],
                "picking_policy": "direct",
                "shopinvader_backend_id": cls.backend.id,
            }
        )
        cls.so3 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_2.id,
                "partner_invoice_id": cls.partner_2.id,
                "partner_shipping_id": cls.partner_2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": p.name,
                            "product_id": p.id,
                            "product_uom_qty": (i + 3) * 2,
                            "product_uom": p.uom_id.id,
                            "price_unit": p.list_price,
                        },
                    )
                    for i, p in enumerate([cls.productA, cls.productB, cls.productC])
                ],
                "picking_policy": "direct",
                "shopinvader_backend_id": cls.backend.id,
            }
        )
        cls.so1.action_confirm()
        cls.so2.action_confirm()
        cls.so3.action_confirm()

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.delivery_move_service = work.component(usage="delivery_moves")
        # We have no session here
        with self.work_on_services(partner=self.partner_2) as work:
            self.service_as_seller = work.component(usage="delivery_moves")

    def test_search_delivery_move_as_customer(self):
        moves = self.delivery_move_service.dispatch(
            "search",
        )["data"]
        # Partner should have 4 moves:
        self.assertEquals(len(moves), 4)
        self.assertEquals(moves[0]["product"]["name"], "Product A")
        self.assertEquals(moves[0]["sale"]["sale_id"], self.so1.id)
        self.assertEquals(moves[0]["delivery_product_qty"], 10)
        self.assertEquals(moves[1]["product"]["name"], "Product B")
        self.assertEquals(moves[1]["sale"]["sale_id"], self.so1.id)
        self.assertEquals(moves[1]["delivery_product_qty"], 20)
        self.assertEquals(moves[2]["product"]["name"], "Product A")
        self.assertEquals(moves[2]["sale"]["sale_id"], self.so2.id)
        self.assertEquals(moves[2]["delivery_product_qty"], 14)
        self.assertEquals(moves[3]["product"]["name"], "Product C")
        self.assertEquals(moves[3]["sale"]["sale_id"], self.so2.id)
        self.assertEquals(moves[3]["delivery_product_qty"], 7)

    def test_search_delivery_move_as_customer_2(self):
        moves = self.service_as_seller.dispatch(
            "search",
        )["data"]
        # Partner 2 should have 3 moves:
        self.assertEquals(len(moves), 3)
        self.assertEquals(moves[0]["product"]["name"], "Product A")
        self.assertEquals(moves[0]["sale"]["sale_id"], self.so3.id)
        self.assertEquals(moves[0]["delivery_product_qty"], 6)
        self.assertEquals(moves[1]["product"]["name"], "Product B")
        self.assertEquals(moves[1]["sale"]["sale_id"], self.so3.id)
        self.assertEquals(moves[1]["delivery_product_qty"], 8)
        self.assertEquals(moves[2]["product"]["name"], "Product C")
        self.assertEquals(moves[2]["sale"]["sale_id"], self.so3.id)
        self.assertEquals(moves[2]["delivery_product_qty"], 10)

    def test_search_delivery_move_as_seller(self):
        with self.seller_group():
            moves = self.service_as_seller.dispatch(
                "search",
            )["data"]

        # As seller partner 2 should have its 3 moves and the ones from its sell of so2:

        self.assertEquals(len(moves), 5)
        self.assertEquals(moves[0]["product"]["name"], "Product A")
        self.assertEquals(moves[0]["sale"]["sale_id"], self.so2.id)
        self.assertEquals(moves[0]["delivery_product_qty"], 14)
        self.assertEquals(moves[1]["product"]["name"], "Product C")
        self.assertEquals(moves[1]["sale"]["sale_id"], self.so2.id)
        self.assertEquals(moves[1]["delivery_product_qty"], 7)
        self.assertEquals(moves[2]["product"]["name"], "Product A")
        self.assertEquals(moves[2]["sale"]["sale_id"], self.so3.id)
        self.assertEquals(moves[2]["delivery_product_qty"], 6)
        self.assertEquals(moves[3]["product"]["name"], "Product B")
        self.assertEquals(moves[3]["sale"]["sale_id"], self.so3.id)
        self.assertEquals(moves[3]["delivery_product_qty"], 8)
        self.assertEquals(moves[4]["product"]["name"], "Product C")
        self.assertEquals(moves[4]["sale"]["sale_id"], self.so3.id)
        self.assertEquals(moves[4]["delivery_product_qty"], 10)

    def test_search_delivery_move_as_seller_with_customer_filter(self):
        with self.seller_group():
            moves = self.service_as_seller.dispatch(
                "search", params={"customer_id": self.partner.id}
            )["data"]

        # As seller partner 2 should have the moves from its sell of so2:

        self.assertEquals(len(moves), 2)
        self.assertEquals(moves[0]["product"]["name"], "Product A")
        self.assertEquals(moves[0]["sale"]["sale_id"], self.so2.id)
        self.assertEquals(moves[0]["delivery_product_qty"], 14)
        self.assertEquals(moves[1]["product"]["name"], "Product C")
        self.assertEquals(moves[1]["sale"]["sale_id"], self.so2.id)
        self.assertEquals(moves[1]["delivery_product_qty"], 7)

    def test_search_delivery_move_as_customer_with_customer_filter(self):
        with self.assertRaises(AccessDenied) as e:
            self.delivery_move_service.dispatch(
                "search", params={"customer_id": self.partner_2.id}
            )["data"]
        self.assertEquals(
            str(e.exception), "customer_id filter is only available for seller group"
        )

    def test_search_delivery_move_as_seller_bad_group(self):
        with self.seller_group("buyer"):
            moves = self.service_as_seller.dispatch(
                "search",
            )["data"]
        # Partner 2 should have 3 moves:
        self.assertEquals(len(moves), 3)
        self.assertEquals(moves[0]["product"]["name"], "Product A")
        self.assertEquals(moves[0]["sale"]["sale_id"], self.so3.id)
        self.assertEquals(moves[0]["delivery_product_qty"], 6)
        self.assertEquals(moves[1]["product"]["name"], "Product B")
        self.assertEquals(moves[1]["sale"]["sale_id"], self.so3.id)
        self.assertEquals(moves[1]["delivery_product_qty"], 8)
        self.assertEquals(moves[2]["product"]["name"], "Product C")
        self.assertEquals(moves[2]["sale"]["sale_id"], self.so3.id)
        self.assertEquals(moves[2]["delivery_product_qty"], 10)

    def test_search_delivery_move_as_seller_bad_group_with_custom_filter(self):
        with self.assertRaises(AccessDenied) as e:
            with self.seller_group("buyer"):
                self.service_as_seller.dispatch(
                    "search", params={"customer_id": self.partner_2.id}
                )["data"]
        self.assertEquals(
            str(e.exception), "customer_id filter is only available for seller group"
        )
