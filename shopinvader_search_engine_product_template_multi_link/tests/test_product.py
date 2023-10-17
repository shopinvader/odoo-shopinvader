# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import TestProductLinkCase


class TestProductLink(TestProductLinkCase):
    def _assert_links(self, binding, expected):
        binding.with_context(index=self.se_index).recompute_json()
        self.assertEqual(binding.data["links"], expected)

    def test_links(self):
        # the result is the same for each product and it matches the main variant only
        main1 = self.template_1.product_variant_ids.filtered(lambda x: x.main)
        main2 = self.template_2.product_variant_ids.filtered(lambda x: x.main)
        main3 = self.template_3.product_variant_ids.filtered(lambda x: x.main)

        expected = {
            "up_selling": [{"id": main2.id}],
            "cross_selling": [{"id": main3.id}],
        }
        self._assert_links(self.variant_1_1_binding, expected)
        self._assert_links(self.variant_1_2_binding, expected)

        expected = {
            "cross_selling": [{"id": main3.id}],
            "up_selling": [{"id": main1.id}],
        }
        self._assert_links(self.variant_2_1_binding, expected)
        self._assert_links(self.variant_2_2_binding, expected)

        expected = {
            "cross_selling": [
                {"id": main1.id},
                {"id": main2.id},
            ],
        }
        expected["one_way"] = [{"id": main2.id}]
        self._assert_links(self.variant_3_1_binding, expected)
        self._assert_links(self.variant_3_2_binding, expected)
