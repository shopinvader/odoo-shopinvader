# Copyright 2024 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.tests import SavepointCase

from .common import Mixin


class ProductMediaCase(SavepointCase, Mixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref("product.product_product_4_product_template")
        cls.product_a = cls.env.ref("product.product_product_4")
        cls.product_b = cls.env.ref("product.product_product_4b")
        cls.product_c = cls.env.ref("product.product_product_4c")
        cls.media1 = cls._create_storage_media("test-media.pdf")
        cls.media2 = cls._create_storage_media("test-media.txt")
        cls.media3 = cls._create_storage_media("test-media.csv")
        cls.s_variant = cls.env["shopinvader.variant"].create(
            {"record_id": cls.product_a.id}
        )

    # FIXME
    def test_availability(self):
        self.assertEqual(len(self.s_variant.variant_media_ids), 0)
        rel1 = self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media1.id}
        )
        self.assertEqual(len(self.s_variant.variant_media_ids), 1)
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media2.id}
        )
        self.assertEqual(len(self.s_variant.variant_media_ids), 2)
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media3.id}
        )
        self.assertEqual(len(self.s_variant.variant_media_ids), 3)
        rel1.media_id.active = False
        self.assertEqual(len(self.s_variant.variant_media_ids), 2)
