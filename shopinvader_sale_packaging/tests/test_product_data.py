# Copyright 2020 Camptocamp SA
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestProductPackagingData(CommonCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = product = cls.env.ref("product.product_product_6")
        cls.type_retail_box = cls.env["product.packaging.type"].create(
            {"name": "Retail Box", "code": "PACK", "sequence": 3}
        )
        cls.type_transport_box = cls.env["product.packaging.type"].create(
            {"name": "Transport Box", "code": "CASE", "sequence": 4}
        )
        cls.type_pallet = cls.env["product.packaging.type"].create(
            {"name": "Pallet", "code": "PALLET", "sequence": 5}
        )
        cls.pkg_box = cls.env["product.packaging"].create(
            {
                "name": "Box",
                "product_id": product.id,
                "qty": 50,
                "packaging_type_id": cls.type_retail_box.id,
            }
        )
        cls.pkg_big_box = cls.env["product.packaging"].create(
            {
                "name": "Big Box",
                "product_id": product.id,
                "qty": 200,
                "packaging_type_id": cls.type_transport_box.id,
            }
        )
        cls.pkg_pallet = cls.env["product.packaging"].create(
            {
                "name": "Pallet",
                "product_id": product.id,
                "qty": 2000,
                "packaging_type_id": cls.type_pallet.id,
            }
        )
        cls._bind_products(cls, product)
        cls.shop_variant = product.shopinvader_bind_ids[0]
        # Let it compute once
        cls.shop_variant._compute_packaging()

    def _default_expected(self):
        return [
            {
                "id": self.pkg_pallet.id,
                "name": self.type_pallet.name,
                "qty": self.pkg_pallet.qty,
                "is_unit": False,
                "contained": [
                    {
                        "id": self.pkg_big_box.id,
                        "is_unit": False,
                        "name": self.type_transport_box.name,
                        "qty": 10,
                    }
                ],
            },
            {
                "id": self.pkg_big_box.id,
                "name": self.type_transport_box.name,
                "qty": self.pkg_big_box.qty,
                "is_unit": False,
                "contained": [
                    {
                        "id": self.pkg_box.id,
                        "is_unit": False,
                        "name": self.type_retail_box.name,
                        "qty": 4,
                    }
                ],
            },
            {
                "id": self.pkg_box.id,
                "name": self.type_retail_box.name,
                "qty": self.pkg_box.qty,
                "is_unit": False,
                "contained": [
                    {
                        "id": self.product.uom_id.id,
                        "is_unit": True,
                        "name": self.product.uom_id.name,
                        "qty": 50,
                    }
                ],
            },
            {
                "id": self.product.uom_id.id,
                "is_unit": True,
                "name": self.product.uom_id.name,
                "contained": None,
                "qty": 1.0,
            },
        ]

    def test_product_data(self):
        expected = self._default_expected()
        self.assertEqual(self.shop_variant.packaging, expected)

    def test_product_data_recompute1(self):
        # ensure it gets recomputed if packaging params change
        self.type_pallet.name = "BLA BLA"
        expected = self._default_expected()
        expected[0]["name"] = "BLA BLA"
        self.assertEqual(self.shop_variant.packaging, expected)

    def test_product_data_recompute2(self):
        # ensure it gets recomputed if packaging params change
        self.pkg_box.qty = 20
        self.pkg_big_box.qty = 400
        expected = self._default_expected()
        expected[0]["contained"][0]["qty"] = 5.0
        expected[1]["qty"] = 400.0
        expected[1]["contained"][0]["qty"] = 20.0
        expected[2]["contained"][0]["qty"] = 20.0
        self.assertEqual(self.shop_variant.packaging, expected)
