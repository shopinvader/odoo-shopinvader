# Copyright 2020 Camptocamp SA
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import CommonCase
from odoo.addons.shopinvader.tests.test_cart_item import ItemCaseMixin


class ConnectedItemCase(ItemCaseMixin, CommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_products()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.cart = cls.env.ref("shopinvader.sale_order_2")
        cls.pkg_box = cls.env["product.packaging"].create(
            {"name": "Box", "product_id": cls.product_1.id, "qty": 50}
        )
        cls.pkg_big_box = cls.env["product.packaging"].create(
            {"name": "Big Box", "product_id": cls.product_1.id, "qty": 200}
        )
        cls.pkg_pallet = cls.env["product.packaging"].create(
            {"name": "Pallet", "product_id": cls.product_1.id, "qty": 2000}
        )
        # This module adds new keys: recompute
        cls._refresh_json_data(
            cls, cls.cart.mapped("order_line.product_id") + cls.product_1
        )

    def setUp(self):
        super().setUp()
        self.shopinvader_session = {"cart_id": self.cart.id}
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def test_add_item(self):
        self.remove_cart()
        last_order = self.env["sale.order"].search(
            [], limit=1, order="id desc"
        )
        # TODO: in theory we should be able to skip prod qty
        # since it's computed in `sale_order_line_packaging_qty `
        cart = self.add_item(
            self.product_1.id,
            1,
            packaging_id=self.pkg_pallet,
            packaging_qty=2.0,
        )
        self.assertGreater(cart["id"], last_order.id)
        self.assertEqual(len(cart["lines"]["items"]), 1)
        self.assertEqual(cart["lines"]["count"], 4000)
        cart_line = cart["lines"]["items"][0]
        # check SO line values
        line = self.env["sale.order.line"].browse(cart_line["id"])
        self.assertEqual(line.product_packaging, self.pkg_pallet)
        self.assertEqual(line.product_packaging_qty, 2.0)
        self.assertEqual(line.product_uom_qty, 4000)
        # Check cart line values
        self.check_product_and_qty(cart_line, self.product_1.id, 4000)
        self.assertEqual(
            cart_line["packaging"],
            {
                "id": self.pkg_pallet.id,
                "name": self.pkg_pallet.packaging_type_id.name,
                "code": self.pkg_pallet.packaging_type_id.code,
            },
        )
        self.assertEqual(cart_line["packaging_qty"], 2)
        self.assertIn("sell_only_by_packaging", cart_line["product"])

    def test_update_item(self):
        line = self.cart.order_line[0]
        product = line.product_id
        cart = self.update_item(
            line.id, 1, packaging_id=self.pkg_pallet, packaging_qty=3.0
        )
        # check SO line values
        self.assertEqual(line.product_packaging, self.pkg_pallet)
        self.assertEqual(line.product_packaging_qty, 3.0)
        self.assertEqual(line.product_uom_qty, 6000)
        # Check cart line values
        cart_line = [x for x in cart["lines"]["items"] if x["id"] == line.id][
            0
        ]
        self.check_product_and_qty(cart_line, product.id, 6000)
        self.assertEqual(
            cart_line["packaging"],
            {
                "id": self.pkg_pallet.id,
                "name": self.pkg_pallet.packaging_type_id.name,
                "code": self.pkg_pallet.packaging_type_id.code,
            },
        )
        self.assertEqual(cart_line["packaging_qty"], 3.0)
        self.assertIn("sell_only_by_packaging", cart_line["product"])

    def test_copy_line(self):
        line = self.cart.order_line[0]
        product = line.product_id
        line.write(
            {
                "product_packaging": self.pkg_pallet.id,
                "product_packaging_qty": 4.0,
            }
        )
        self.assertEqual(line.product_uom_qty, 8000)
        cart = self.extract_cart(
            self.service.dispatch("copy", params={"id": self.cart.id})
        )
        cart_line = [
            x
            for x in cart["lines"]["items"]
            if x["product"]["objectID"] == product.id
        ][0]
        self.assertIn("sell_only_by_packaging", cart_line["product"])
        self.check_product_and_qty(cart_line, product.id, 8000)
        # Check cart line values
        self.assertEqual(
            cart_line["packaging"],
            {
                "id": self.pkg_pallet.id,
                "name": self.pkg_pallet.packaging_type_id.name,
                "code": self.pkg_pallet.packaging_type_id.code,
            },
        )
        self.assertEqual(cart_line["packaging_qty"], 4.0)
        # check SO line values
        line = self.env["sale.order.line"].browse(cart_line["id"])
        self.assertEqual(line.product_packaging, self.pkg_pallet)
        self.assertEqual(line.product_packaging_qty, 4.0)
        self.assertEqual(line.product_uom_qty, 8000)

    # TODO: add tests for packaging computation
