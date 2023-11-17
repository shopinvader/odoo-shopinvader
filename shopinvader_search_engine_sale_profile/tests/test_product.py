# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import SaleProfileBackendCommonCase


class TestProductProduct(SaleProfileBackendCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.index = cls.env["se.index"].create(
            {
                "name": "product",
                "backend_id": cls.backend.id,
                "model_id": cls.env.ref("product.model_product_product").id,
                "serializer_type": "shopinvader_product_exports",
            }
        )
        cls.product = cls.env.ref("product.product_product_4b")
        cls.product.write(
            {
                "taxes_id": [
                    (
                        6,
                        0,
                        [cls.env.ref("shopinvader_sale_profile.tax_1").id],
                    )
                ]
            }
        )
        cls.product_binding = cls.product._add_to_index(cls.index)

    def _check_price(self, computed_price, expected_price):
        for key, expected_value in expected_price.items():
            self.assertIn(key, computed_price.keys())
            price_value = computed_price[key]
            for value_key, expected_value in expected_value.items():
                self.assertEqual(expected_value, price_value[value_key])

    def test_price_with_sale_profile(self):
        """
        Test if price field is correctly computed
        :return: bool
        """
        expected_price = {
            "public_tax_exc": {"tax_included": False, "value": 652.17},
            "public_tax_inc": {"tax_included": True, "value": 750.0},
            "pro_tax_exc": {"tax_included": False, "value": 521.74},
        }
        self.product_binding.recompute_json()
        computed_price = self.product_binding.data["price"]
        self._check_price(computed_price, expected_price)
