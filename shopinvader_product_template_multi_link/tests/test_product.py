# -*- coding: utf-8 -*-
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.tests.common import ProductCommonCase


class ProductCase(ProductCommonCase):
    def test_cross_sellings_link(self):
        self.backend.bind_all_category()
        template_1 = self.env.ref("product.product_product_7_product_template")
        template_2 = self.env.ref("product.product_product_9_product_template")
        res = template_1.shopinvader_bind_ids[0].cross_selling_ids
        self.assertEqual(len(res), 1)
        self.assertEqual(
            res, template_2.shopinvader_bind_ids[0].shopinvader_variant_ids
        )
