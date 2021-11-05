# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class BindingCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env["product.template"].create({"name": "Test"})
        cls.product = cls.template.product_variant_ids
        cls.shopinvader_product = (
            cls.env["shopinvader.product"]
            .with_context(map_children=True)
            .create(
                {
                    "record_id": cls.template.id,
                    "backend_id": cls.env.ref("shopinvader.backend_1").id,
                    "lang_id": cls.env.ref("base.lang_en").id,
                }
            )
        )
        cls.shopinvader_variant = cls.shopinvader_product.shopinvader_variant_ids


class BindingDoneCase(BindingCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.shopinvader_variant.write({"sync_state": "done"})

    def test_unlink_shopinvader_product(self):
        self.shopinvader_product.unlink()

    def test_unlink_product_product(self):
        self.product.unlink()

    def test_unlink_product_template(self):
        self.template.unlink()


class BindingInactiveDoneCase(BindingCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.shopinvader_variant.active = False
        cls.shopinvader_variant.sync_state = "done"

    def test_unlink_shopinvader_product(self):
        self.shopinvader_product.unlink()

    def test_unlink_product_product(self):
        self.product.unlink()

    def test_unlink_product_template(self):
        self.template.unlink()
