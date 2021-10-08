# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductBrandCommonCase(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["product.brand"].create({"name": "Foo Brand"})
        cls.lang_en = cls.env.ref("base.lang_en")
        cls.binding = cls.env["shopinvader.brand"].create(
            {
                "backend_id": cls.backend.id,
                "lang_id": cls.lang_en.id,
                "record_id": cls.brand.id,
                "active": True,
            }
        )
