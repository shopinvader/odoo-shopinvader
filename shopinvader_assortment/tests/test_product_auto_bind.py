# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestProductAutoBind(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                test_queue_job_no_delay=True,
            )
        )
        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.variant_obj = cls.env["shopinvader.variant"]
        cls.product_obj = cls.env["product.product"]
        cls.backend.product_assortment_id.domain = "[('sale_ok', '=', True)]"

    def test_shopinvader_auto_product_auto_bind(self):
        # Test bind all products from assortment domain
        variants = self.variant_obj.search(
            [("backend_id", "=", self.backend.id)]
        )
        self.assertFalse(variants)
        domain = self.backend.product_assortment_id._get_eval_domain()
        products_to_bind = self.product_obj.search(domain)

        self.backend.autobind_product_from_assortment()

        variants = self.variant_obj.search(
            [("backend_id", "=", self.backend.id)]
        )

        self.assertEqual(
            sorted(products_to_bind.ids),
            sorted(variants.mapped("record_id").ids),
        )

        # Exclude one product, related binding should be inactivated
        excluded_product = self.env.ref("product.product_product_7")
        self.backend.product_assortment_id.write(
            {"blacklist_product_ids": [(4, excluded_product.id)]}
        )

        self.backend.autobind_product_from_assortment()

        excluded_variant = self.variant_obj.with_context(
            active_test=False
        ).search(
            [
                ("backend_id", "=", self.backend.id),
                ("record_id", "=", excluded_product.id),
            ]
        )
        self.assertTrue(excluded_variant)
        self.assertFalse(excluded_variant.active)
        variants = self.variant_obj.search(
            [("backend_id", "=", self.backend.id)]
        )
        self.assertEqual(len(variants), len(products_to_bind) - 1)

        # remove product from blacklist, related binding should reactivated
        self.backend.product_assortment_id.write(
            {"blacklist_product_ids": [(5, False, False)]}
        )

        self.backend.autobind_product_from_assortment()

        excluded_variant = self.variant_obj.search(
            [
                ("backend_id", "=", self.backend.id),
                ("record_id", "=", excluded_product.id),
            ]
        )
        self.assertTrue(excluded_variant)

    def test_shopinvader_force_product_auto_bind(self):
        # Test bind all products from assortment domain
        variants = self.variant_obj.search(
            [("backend_id", "=", self.backend.id)]
        )
        self.assertFalse(variants)
        domain = self.backend.product_assortment_id._get_eval_domain()
        products_to_bind = self.product_obj.search(domain)

        self.backend.force_recompute_all_binding_index()

        variants = self.variant_obj.search(
            [("backend_id", "=", self.backend.id)]
        )

        self.assertEqual(
            sorted(products_to_bind.ids),
            sorted(variants.mapped("record_id").ids),
        )

        # Exclude one product, related binding should be inactivated
        excluded_product = self.env.ref("product.product_product_7")
        self.backend.product_assortment_id.write(
            {"blacklist_product_ids": [(4, excluded_product.id)]}
        )

        self.backend.force_recompute_all_binding_index()

        excluded_variant = self.variant_obj.with_context(
            active_test=False
        ).search(
            [
                ("backend_id", "=", self.backend.id),
                ("record_id", "=", excluded_product.id),
            ]
        )
        self.assertTrue(excluded_variant)
        self.assertFalse(excluded_variant.active)
        variants = self.variant_obj.search(
            [("backend_id", "=", self.backend.id)]
        )
        self.assertEqual(len(variants), len(products_to_bind) - 1)

        # remove product from blacklist, related binding should reactivated
        self.backend.product_assortment_id.write(
            {"blacklist_product_ids": [(5, False, False)]}
        )

        self.backend.force_recompute_all_binding_index()

        excluded_variant = self.variant_obj.search(
            [
                ("backend_id", "=", self.backend.id),
                ("record_id", "=", excluded_product.id),
            ]
        )
        self.assertTrue(excluded_variant)
