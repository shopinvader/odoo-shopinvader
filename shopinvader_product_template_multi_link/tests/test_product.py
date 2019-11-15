# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template_1 = cls.env.ref(
            "product.product_product_7_product_template"
        )
        cls.template_2 = cls.env.ref(
            "product.product_product_9_product_template"
        )
        cls.template_1.product_template_link_ids.unlink()
        cls.up_selling_link = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_1.id,
                "right_product_tmpl_id": cls.template_2.id,
                "type_id": cls.env.ref(
                    "product_template_multi_link."
                    "product_template_link_type_up_selling"
                ).id,
            }
        )
        cls.cross_selling_link = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_1.id,
                "right_product_tmpl_id": cls.template_2.id,
                "type_id": cls.env.ref(
                    "product_template_multi_link."
                    "product_template_link_type_cross_selling"
                ).id,
            }
        )

    def test_cross_sellings_link(self):
        res = self.template_1.shopinvader_bind_ids[0].cross_selling_ids
        self.assertEqual(len(res), 1)
        self.assertEqual(
            res,
            self.template_2.shopinvader_bind_ids[0].shopinvader_variant_ids,
        )

    def test_up_sellings_link(self):
        res = self.template_1.shopinvader_bind_ids[0].up_selling_ids
        self.assertEqual(len(res), 1)
        self.assertEqual(
            res,
            self.template_2.shopinvader_bind_ids[0].shopinvader_variant_ids,
        )
