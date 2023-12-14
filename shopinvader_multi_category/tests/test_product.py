# Copyright 2017-2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.tests.test_product import ProductCase


class TestProductCase(ProductCase):
    def test_product_shopinvader_categories(self):
        self.assertEqual(len(self.variant.shopinvader_categ_ids), 3)
        self.variant.categ_ids += self.env.ref(
            "shopinvader_product.product_category_23"
        )
        self.assertEqual(len(self.variant.shopinvader_categ_ids), 4)
