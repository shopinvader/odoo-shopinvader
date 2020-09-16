# -*- coding: utf-8 -*-
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductLinkCaseBase(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super(ProductLinkCaseBase, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                # compatibility flag when you run tests on a db
                # where `product_variant_multi_link` is installed.
                _product_variant_link_bypass_check=True,
            )
        )
        cls.template_1 = cls.env.ref(
            "shopinvader.product_product_39_product_template"
        )
        cls.template_1.product_template_link_ids.unlink()
        cls.template_2 = cls.env.ref(
            "shopinvader.product_product_42_product_template"
        )
        cls.template_2.product_template_link_ids.unlink()
        cls.template_3 = cls.env.ref(
            "shopinvader.product_product_45_product_template"
        )
        cls.template_3.product_template_link_ids.unlink()

        cls.variant_1_1 = cls.template_1.product_variant_ids[0]
        cls.variant_1_2 = cls.template_1.product_variant_ids[1]
        cls.variant_2_1 = cls.template_2.product_variant_ids[0]
        cls.variant_2_2 = cls.template_2.product_variant_ids[1]
        cls.variant_3_1 = cls.template_3.product_variant_ids[0]
        cls.variant_3_2 = cls.template_3.product_variant_ids[1]
        cls.shopinvader_variant_1_1 = cls.variant_1_1._get_invader_variant(
            cls.backend, "en_US"
        )
        cls.shopinvader_variant_1_2 = cls.variant_1_2._get_invader_variant(
            cls.backend, "en_US"
        )
        cls.shopinvader_variant_2_1 = cls.variant_2_1._get_invader_variant(
            cls.backend, "en_US"
        )
        cls.shopinvader_variant_2_2 = cls.variant_2_2._get_invader_variant(
            cls.backend, "en_US"
        )
        cls.shopinvader_variant_3_1 = cls.variant_3_1._get_invader_variant(
            cls.backend, "en_US"
        )
        cls.shopinvader_variant_3_2 = cls.variant_3_2._get_invader_variant(
            cls.backend, "en_US"
        )

        cls._create_links()

    @classmethod
    def _create_links(cls):
        cls.link_upselling_1_2 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_1.id,
                "right_product_tmpl_id": cls.template_2.id,
                "type_id": cls.env.ref(
                    "product_template_multi_link."
                    "product_template_link_type_up_selling"
                ).id,
            }
        )
        cls.link_crosselling_1_3 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_1.id,
                "right_product_tmpl_id": cls.template_3.id,
                "type_id": cls.env.ref(
                    "product_template_multi_link."
                    "product_template_link_type_cross_selling"
                ).id,
            }
        )
        cls.link_crosselling_2_3 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_2.id,
                "right_product_tmpl_id": cls.template_3.id,
                "type_id": cls.env.ref(
                    "product_template_multi_link."
                    "product_template_link_type_cross_selling"
                ).id,
            }
        )


class ProductLinkCase(ProductLinkCaseBase):
    def test_links(self):
        # the result is the same for each product and it matches the main variant only
        main1 = self.template_1.mapped(
            "shopinvader_bind_ids.shopinvader_variant_ids"
        ).filtered(lambda x: x.main)
        main2 = self.template_2.mapped(
            "shopinvader_bind_ids.shopinvader_variant_ids"
        ).filtered(lambda x: x.main)
        main3 = self.template_3.mapped(
            "shopinvader_bind_ids.shopinvader_variant_ids"
        ).filtered(lambda x: x.main)

        expected = {
            "up_selling": [{"id": main2.record_id.id}],
            "cross_selling": [{"id": main3.record_id.id}],
        }
        self.assertEqual(
            self.shopinvader_variant_1_1.shopinvader_product_id.product_links,
            expected,
        )
        self.assertEqual(
            self.shopinvader_variant_1_2.shopinvader_product_id.product_links,
            expected,
        )

        expected = {
            "cross_selling": [{"id": main3.record_id.id}],
            "up_selling": [{"id": main1.record_id.id}],
        }
        self.assertEqual(
            self.shopinvader_variant_2_1.shopinvader_product_id.product_links,
            expected,
        )
        self.assertEqual(
            self.shopinvader_variant_2_2.shopinvader_product_id.product_links,
            expected,
        )

    def test_link_json_data(self):
        exporter = self.env.ref("shopinvader.ir_exp_shopinvader_variant")
        parser = exporter.get_json_parser()
        self.assertIn("links", self.shopinvader_variant_2_2.jsonify(parser)[0])
