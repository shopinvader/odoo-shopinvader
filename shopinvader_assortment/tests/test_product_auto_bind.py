# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBaseFake


class TestProductAutoBind(TestBindingIndexBaseFake):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_obj = cls.env["product.product"]
        cls.backend.product_assortment_id = cls.env.ref(
            "shopinvader_assortment.shopinvader_assortment1"
        )
        cls.backend.product_manual_binding = False
        cls.backend.product_assortment_id.domain = "[('sale_ok', '=', True)]"
        cls.product_index = cls.env["se.index"].create(
            {
                "name": "product",
                "backend_id": cls.backend.id,
                "model_id": cls.env.ref("product.model_product_product").id,
                "serializer_type": "shopinvader_product_exports",
            }
        )

    def test_shopinvader_auto_product_auto_bind(self):
        # Test bind all products from assortment domain
        self.assertFalse(self.product_index.binding_ids)
        domain = self.backend.product_assortment_id._get_eval_domain()
        products_to_bind = self.product_obj.search(domain)

        self.backend.autobind_product_from_assortment()
        self.assertTrue(self.product_index.binding_ids)
        self.assertEqual(products_to_bind, self.product_index.binding_ids.record)

        # Exclude one product, related binding should be inactivated
        excluded_product = self.env.ref("product.product_product_7")
        self.backend.product_assortment_id.blacklist_product_ids = excluded_product

        self.backend.autobind_product_from_assortment()
        self.assertEqual(excluded_product.se_binding_ids.state, "to_delete")

        # remove product from blacklist, related binding should reactivated
        self.backend.product_assortment_id.blacklist_product_ids = False

        self.backend.autobind_product_from_assortment()
        self.assertEqual(excluded_product.se_binding_ids.state, "to_recompute")
