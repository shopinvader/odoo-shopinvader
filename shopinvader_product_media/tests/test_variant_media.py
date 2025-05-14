# Copyright 2024 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.addons.shopinvader.tests.common import ProductCommonCase

from .common import Mixin


class ProductMediaCase(ProductCommonCase, Mixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media1 = cls._create_storage_media("test-media.pdf")
        cls.media2 = cls._create_storage_media("test-media.txt")
        cls.media3 = cls._create_storage_media("test-media.csv")

    def test_availability(self):
        self.assertEqual(len(self.shopinvader_variant.variant_media_ids), 0)
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media1.id}
        )
        self.assertEqual(
            self.shopinvader_variant.variant_media_ids.media_id, self.media1
        )
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media2.id}
        )
        self.assertEqual(
            self.shopinvader_variant.variant_media_ids.media_id,
            self.media1 | self.media2,
        )
        self.env["product.media.relation"].create(
            {"product_tmpl_id": self.template.id, "media_id": self.media3.id}
        )
        self.assertEqual(
            self.shopinvader_variant.variant_media_ids.media_id,
            self.media1 | self.media2 | self.media3,
        )
        self.media1.active = False
        self.assertEqual(
            self.shopinvader_variant.variant_media_ids.media_id,
            self.media2 | self.media3,
        )
