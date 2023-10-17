# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader_search_engine.tests.common import (
    TestBindingIndexBase,
    TestProductBindingMixin,
)


class TestProductLinkMixin(TestProductBindingMixin):
    @classmethod
    def setup_records(cls, tst_cls, backend=None):  # pylint: disable=missing-return
        super().setup_records(tst_cls, backend=backend)
        tst_cls.template_1 = tst_cls.env.ref(
            "shopinvader_product.product_template_armchair_mid_century"
        )
        tst_cls.template_1.product_template_link_ids.unlink()
        tst_cls.template_2 = tst_cls.env.ref(
            "shopinvader_product.product_template_chair_mid_century"
        )
        tst_cls.template_2.product_template_link_ids.unlink()
        tst_cls.template_3 = tst_cls.env.ref(
            "shopinvader_product.product_template_tv_cabinet_shaker_wood"
        )
        tst_cls.template_3.product_template_link_ids.unlink()

        tst_cls.variant_1_1 = tst_cls.template_1.product_variant_ids[0]
        tst_cls.variant_1_2 = tst_cls.template_1.product_variant_ids[1]
        tst_cls.variant_2_1 = tst_cls.template_2.product_variant_ids[0]
        tst_cls.variant_2_2 = tst_cls.template_2.product_variant_ids[1]
        tst_cls.variant_3_1 = tst_cls.template_3.product_variant_ids[0]
        tst_cls.variant_3_2 = tst_cls.template_3.product_variant_ids[1]
        tst_cls.link_type_asym = tst_cls.env["product.template.link.type"].create(
            {"name": "One way link", "code": "one-way", "is_symmetric": False}
        )
        tst_cls.cross_selling_type = tst_cls.env[
            "product.template.link.type"
        ].get_by_code("cross-selling")
        tst_cls.up_selling_type = tst_cls.env["product.template.link.type"].get_by_code(
            "up-selling"
        )
        cls._create_links(tst_cls)
        tst_cls.variant_1_1_binding = tst_cls.variant_1_1._add_to_index(
            tst_cls.se_index
        )
        tst_cls.variant_1_2_binding = tst_cls.variant_1_2._add_to_index(
            tst_cls.se_index
        )
        tst_cls.variant_2_1_binding = tst_cls.variant_2_1._add_to_index(
            tst_cls.se_index
        )
        tst_cls.variant_2_2_binding = tst_cls.variant_2_2._add_to_index(
            tst_cls.se_index
        )
        tst_cls.variant_3_1_binding = tst_cls.variant_3_1._add_to_index(
            tst_cls.se_index
        )
        tst_cls.variant_3_2_binding = tst_cls.variant_3_2._add_to_index(
            tst_cls.se_index
        )

    @classmethod
    def _create_links(cls, tst_cls):
        tst_cls.link_upselling_1_2 = tst_cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": tst_cls.template_1.id,
                "right_product_tmpl_id": tst_cls.template_2.id,
                "type_id": tst_cls.up_selling_type.id,
            }
        )
        tst_cls.link_crosselling_1_3 = tst_cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": tst_cls.template_1.id,
                "right_product_tmpl_id": tst_cls.template_3.id,
                "type_id": tst_cls.cross_selling_type.id,
            }
        )
        tst_cls.link_crosselling_2_3 = tst_cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": tst_cls.template_2.id,
                "right_product_tmpl_id": tst_cls.template_3.id,
                "type_id": tst_cls.env.ref(
                    "product_template_multi_link."
                    "product_template_link_type_cross_selling"
                ).id,
            }
        )
        tst_cls.link_one_way_3_2 = tst_cls.env["product.template.link"].create(
            {
                "left_product_tmpl_id": tst_cls.template_3.id,
                "right_product_tmpl_id": tst_cls.template_2.id,
                "type_id": tst_cls.link_type_asym.id,
            }
        )


class TestProductLinkCase(TestBindingIndexBase, TestProductLinkMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        TestProductLinkMixin.setup_records(cls)
