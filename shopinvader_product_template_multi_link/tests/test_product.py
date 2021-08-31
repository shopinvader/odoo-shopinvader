# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import ProductLinkCaseBase


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
        expected = {
            "cross_selling": [
                {"id": main1.record_id.id},
                {"id": main2.record_id.id},
            ],
        }
        expected["one_way"] = [{"id": main2.record_id.id}]
        self.assertEqual(
            self.shopinvader_variant_3_2.shopinvader_product_id.product_links,
            expected,
        )

    def test_link_json_data(self):
        exporter = self.env.ref("shopinvader.ir_exp_shopinvader_variant")
        parser = exporter.get_json_parser()
        self.assertIn("links", self.shopinvader_variant_2_2.jsonify(parser, one=True))
