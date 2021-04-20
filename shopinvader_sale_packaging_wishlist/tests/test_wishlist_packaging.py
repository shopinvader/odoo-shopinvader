# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_wishlist.tests.test_wishlist import (
    CommonWishlistCase,
)


class WishlistCase(CommonWishlistCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.prod_set = cls.env.ref("shopinvader_wishlist.wishlist_1")
        cls.prod_set.shopinvader_backend_id = cls.backend
        cls.packaging_type = (
            cls.env["product.packaging.type"]
            .sudo()
            .create({"name": "TYPE 1", "code": "P", "sequence": 3})
        )
        cls.product_packaging = cls.env["product.packaging"].create(
            {
                "name": "PKG TEST",
                "product_id": cls.prod1.id,
                "qty": 4,
                "packaging_type_id": cls.packaging_type.id,
            }
        )
        # Make sure our products' data is up to date
        cls._refresh_json_data(
            cls, cls.prod_set.mapped("set_line_ids.product_id")
        )

    def test_create(self):
        params = dict(self.wl_params)
        params["lines"][0].update(
            {"packaging_id": self.product_packaging.id, "packaging_qty": 2}
        )
        res = self.wishlist_service.dispatch("create", params=params)["data"]
        record = self.env["product.set"].browse(res["id"])
        line = record.set_line_ids.filtered(
            lambda x: x.product_id == self.prod1
        )
        self.assertEqual(line.product_packaging_id, self.product_packaging)
        self.assertEqual(line.product_packaging_qty, 2)
        self.assertEqual(line.quantity, 8)

    def test_update_item1(self):
        prod = self.env.ref("product.product_product_4b")
        self.assertIn(prod, self.prod_set.mapped("set_line_ids.product_id"))
        self._bind_products(prod)
        # This line has no package
        line = self.prod_set.get_lines_by_products(product_ids=prod.ids)
        self.assertEqual(line.quantity, 1)
        # Add package and package qty
        params = {
            "lines": [
                {
                    "product_id": prod.id,
                    "packaging_id": self.product_packaging.id,
                    "packaging_qty": 4,
                }
            ]
        }
        self.wishlist_service.dispatch(
            "update_items", self.prod_set.id, params=params
        )
        self.assertEqual(line.product_packaging_id, self.product_packaging)
        self.assertEqual(line.product_packaging_qty, 4)
        self.assertEqual(line.quantity, 16)
        # Remove package
        params = {
            "lines": [
                {
                    "product_id": prod.id,
                    "quantity": 7,
                    "packaging_qty": 0,
                    "packaging_id": None,
                }
            ]
        }
        self.wishlist_service.dispatch(
            "update_items", self.prod_set.id, params=params
        )
        self.assertFalse(line.product_packaging_id)
        self.assertEqual(line.product_packaging_qty, 0.0)
        self.assertEqual(line.quantity, 7)

    def test_jsonify(self):
        res = self.wishlist_service._to_json_one(self.prod_set)
        res_line = res["lines"][0]
        prod = self.env.ref("product.product_product_4b")
        packaging = self.env["product.packaging"].create(
            {
                "name": "PKG Foo",
                "product_id": prod.id,
                "qty": 100,
                "can_be_sold": False,
                "packaging_type_id": self.packaging_type.id,
            }
        )
        self.assertEqual(res_line["quantity"], 1)
        self.assertEqual(res_line["packaging_qty"], 0.0)
        self.assertEqual(res_line["packaging"], None)
        self.assertEqual(res_line["product"]["sell_only_by_packaging"], False)
        self.assertEqual(
            res_line["packaging_by_qty"],
            [
                {
                    "contained": None,
                    "id": 1,
                    "is_unit": True,
                    "name": "Units",
                    "qty": 1,
                }
            ],
        )

        # set some packaging values
        packaging.can_be_sold = True
        self.prod_set.set_line_ids[0].write(
            {"product_packaging_qty": 3, "product_packaging_id": packaging.id}
        )
        res = self.wishlist_service._to_json_one(self.prod_set)
        res_line = res["lines"][0]
        self.assertEqual(res_line["quantity"], 300)
        self.assertEqual(res_line["packaging_qty"], 3.0)
        self.assertEqual(
            res_line["packaging"],
            {
                "id": packaging.id,
                "name": self.packaging_type.name,
                "code": self.packaging_type.code,
            },
        )
        self.assertEqual(
            res_line["packaging_by_qty"],
            [
                {
                    "contained": [
                        {
                            "id": prod.uom_id.id,
                            "is_unit": True,
                            "name": "Units",
                            "qty": 100,
                        }
                    ],
                    "id": packaging.id,
                    "is_unit": False,
                    "name": packaging.packaging_type_id.name,
                    "qty": 3,
                }
            ],
        )
