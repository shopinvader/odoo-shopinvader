# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import io

from odoo_test_helper import FakeModelLoader
from PIL import Image

from odoo.addons.connector_search_engine.tests.common import TestSeBackendCaseBase
from odoo.addons.extendable.tests.common import ExtendableMixin


class TestSeMultiImageThumbnailCase(TestSeBackendCaseBase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        cls.addClassCleanup(cls.loader.restore_registry)
        from odoo.addons.connector_search_engine.tests.models import SeBackend, SeIndex

        cls.loader.update_registry(
            (
                SeIndex,
                SeBackend,
            )
        )
        cls.backend = cls.env["se.backend"].create(
            {"name": "Fake SE", "tech_name": "fake_se", "backend_type": "fake"}
        )

        # create thumbnail sizes
        cls.size_small = cls.env["se.thumbnail.size"].create(
            {
                "name": "small",
                "key": "small",
                "size_x": 5,
                "size_y": 5,
            }
        )
        cls.size_medium = cls.env["se.thumbnail.size"].create(
            {
                "name": "medium",
                "key": "medium",
                "size_x": 10,
                "size_y": 10,
            }
        )

        # create sizes for categories and products
        cls.env["se.image.field.thumbnail.size"].create(
            {
                "model_id": cls.env.ref("product.model_product_product").id,
                "field_id": cls.env.ref(
                    "fs_product_multi_image.field_product_product__variant_image_ids"
                ).id,
                "backend_id": cls.backend.id,
                "size_ids": [(6, 0, [cls.size_small.id, cls.size_medium.id])],
            }
        )

        cls.env["se.image.field.thumbnail.size"].create(
            {
                "model_id": cls.env.ref("product.model_product_category").id,
                "field_id": cls.env.ref(
                    "fs_product_multi_image.field_product_category__image_ids"
                ).id,
                "backend_id": cls.backend.id,
                "size_ids": [(6, 0, [cls.size_small.id, cls.size_medium.id])],
            }
        )

        # create image tag
        cls.tag1 = cls.env["image.tag"].create(
            {
                "name": "tag1",
            }
        )
        cls.tag2 = cls.env["image.tag"].create(
            {
                "name": "tag2",
            }
        )

        # create index for product and category
        cls.product_index = cls.env["se.index"].create(
            {
                "name": "product",
                "backend_id": cls.backend.id,
                "model_id": cls.env.ref("product.model_product_product").id,
                "serializer_type": "shopinvader_product_exports",
            }
        )
        cls.category_index = cls.env["se.index"].create(
            {
                "name": "category",
                "backend_id": cls.backend.id,
                "model_id": cls.env.ref("product.model_product_category").id,
                "serializer_type": "shopinvader_category_exports",
            }
        )
        cls.white_image = cls._create_image(16, 16, color="#FFFFFF")
        cls.black_image = cls._create_image(16, 16, color="#000000")
        cls.logo_image = cls._create_image(16, 16, color="#FFA500")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
            }
        )
        cls.product_white_image = cls.env["fs.product.image"].create(
            {
                "sequence": 1,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "specific_image": {
                    "filename": "white.png",
                    "content": base64.b64encode(cls.white_image),
                },
                "tag_id": cls.tag1.id,
            }
        )
        cls.product_black_image = cls.env["fs.product.image"].create(
            {
                "sequence": 2,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "specific_image": {
                    "filename": "black.png",
                    "content": base64.b64encode(cls.black_image),
                },
                "tag_id": cls.tag2.id,
            }
        )
        cls.product_binding = cls.product._add_to_index(cls.product_index)

        cls.category = cls.env["product.category"].create(
            {
                "name": "Test category",
            }
        )
        cls.category_logo_image = cls.env["fs.product.category.image"].create(
            {
                "sequence": 1,
                "product_categ_id": cls.category.id,
                "image": {
                    "filename": "logo.png",
                    "content": base64.b64encode(cls.logo_image),
                },
            }
        )
        cls.category_binding = cls.category._add_to_index(cls.category_index)
        # set odoo base_url
        cls.env["ir.config_parameter"].sudo().set_param(
            "web.base.url", "http://localhost:8069"
        )

    def setUp(self):
        super().setUp()
        # fmt: off
        self.fs_storage = self.env["fs.storage"].create(
            {
                "name": "Temp FS Storage",
                "protocol": "memory",
                "code": "mem_dir",
                "directory_path": "/tmp/",
                "model_xmlids": "fs_product_multi_image.model_fs_product_category_image,"
                                "fs_product_multi_image.model_fs_product_image,"
                                "search_engine_image_thumbnail.model_se_thumbnail",
                "base_url": "https://media.alcyonbelux.be/",
                "is_directory_path_in_url": False,
            }
        )
        # fmt: on

    @classmethod
    def _create_image(cls, width, height, color="#4169E1", img_format="PNG"):
        f = io.BytesIO()
        Image.new("RGB", (width, height), color).save(f, img_format)
        f.seek(0)
        return f.read()

    def assert_image_size(self, value: bytes, width, height):
        self.assertEqual(Image.open(io.BytesIO(value)).size, (width, height))
