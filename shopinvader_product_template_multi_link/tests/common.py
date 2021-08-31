# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductLinkCaseBase(ProductCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                # compatibility flag when you run tests on a db
                # where `product_variant_multi_link` is installed.
                _product_variant_link_bypass_check=True,
            )
        )
        cls.template_1 = cls.env.ref(
            "shopinvader.product_template_armchair_mid_century"
        )
        cls.template_1.product_template_link_ids.unlink()
        cls.template_2 = cls.env.ref("shopinvader.product_template_chair_mid_century")
        cls.template_2.product_template_link_ids.unlink()
        cls.template_3 = cls.env.ref(
            "shopinvader.product_template_tv_cabinet_shaker_wood"
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
        cls.link_type_asym = cls.env["product.template.link.type"].create(
            {"name": "One way link", "code": "one-way", "is_symmetric": False}
        )
        cls.cross_selling_type = cls.env["product.template.link.type"].get_by_code(
            "cross-selling"
        )
        cls.up_selling_type = cls.env["product.template.link.type"].get_by_code(
            "up-selling"
        )
        cls._create_links()

    @classmethod
    def _create_links(cls):
        cls.link_upselling_1_2 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_1.id,
                "right_product_tmpl_id": cls.template_2.id,
                "type_id": cls.up_selling_type.id,
            }
        )
        cls.link_crosselling_1_3 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_1.id,
                "right_product_tmpl_id": cls.template_3.id,
                "type_id": cls.cross_selling_type.id,
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
        cls.link_one_way_3_2 = cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": cls.template_3.id,
                "right_product_tmpl_id": cls.template_2.id,
                "type_id": cls.link_type_asym.id,
            }
        )
