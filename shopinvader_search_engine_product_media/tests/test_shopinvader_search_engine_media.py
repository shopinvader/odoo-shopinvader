# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from .common import ProductMediaCase


class TestShopinvaderSearchEngineMedia(ProductMediaCase):
    def test_product_media(self):
        self.backend.media_data_url_strategy = "odoo"
        product = self.product_binding._contextualize(self.product_binding)
        data = self.product_index.model_serializer.serialize(product.record)
        self.assertIn("medias", data)
        self.assertEqual(data["medias"], [])
        media_c = self.env["fs.product.media"].create(
            {
                "product_tmpl_id": self.product_a.product_tmpl_id.id,
                "media_id": self.media_c.id,
                "sequence": 10,
                "link_existing": True,
            }
        )
        data = self.product_index.model_serializer.serialize(product.record)
        self.assertEqual(len(data["medias"]), 1)
        media = data["medias"][0]
        default_expected = self._default_media(media_c)
        media_subset = {
            key: item for key, item in media.items() if key in default_expected.keys()
        }
        self.assertDictEqual(media_subset, default_expected)
