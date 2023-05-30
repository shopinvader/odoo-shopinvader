# Copyright 2020 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.shopinvader_wishlist.tests.test_wishlist import (
    CommonWishlistCase,
)


@tagged("post_install", "-at_install")
class WishlistCase(CommonWishlistCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.prod_set = cls.env.ref("shopinvader_wishlist.wishlist_1")
        cls.prod_set.shopinvader_backend_id = cls.backend
        cls.partner2 = cls.env.ref("shopinvader.partner_2")
        cls.discount_pricelist = cls.env.ref("shopinvader.pricelist_1")
        cls.fiscal_pos1 = cls.env.ref("shopinvader.fiscal_position_0")
        cls.fiscal_pos2 = cls.env.ref("shopinvader.fiscal_position_2")
        cls.base_pricelist = cls.env.ref("product.list0")
        cls.pricelist_field = cls.env.ref(
            "product.field_res_partner__property_product_pricelist"
        )
        cls.backend.cart_pricelist_partner_field_id = cls.pricelist_field

        prod = cls.env.ref("product.product_product_4b")
        cls.s_variant = prod.shopinvader_bind_ids[0]

    def _get_service(self, partner):
        with self.work_on_services(partner=partner) as work:
            return work.component(usage="customer_price")

    def _get_line_data(self):
        return self.wishlist_service._to_json_one(self.prod_set)["lines"][0]

    def test_jsonify_default(self):
        res_line = self._get_line_data()
        expected_price = self.s_variant._get_price(
            self.base_pricelist, self.fiscal_pos1
        )
        self.assertEqual(res_line["product"]["price"]["default"], expected_price)
        # change partner
        self.wishlist_service.work.partner = self.partner2
        res_line = self.wishlist_service._to_json_one(self.prod_set)["lines"][0]
        self.assertEqual(res_line["product"]["price"]["default"], expected_price)

    def test_jsonify_custom_pricelist(self):
        self.partner.property_product_pricelist = self.discount_pricelist
        expected_price = self.s_variant._get_price(
            self.discount_pricelist, self.fiscal_pos1
        )
        res_line = self._get_line_data()
        self.assertEqual(res_line["product"]["price"]["default"], expected_price)

        # change partner
        self.wishlist_service.work.partner = self.partner2
        res_line = self._get_line_data()
        expected_price = self.s_variant._get_price(
            self.base_pricelist, self.fiscal_pos1
        )
        self.assertEqual(res_line["product"]["price"]["default"], expected_price)

    def test_jsonify_missing_binding(self):
        self.prod_set.set_line_ids.mapped("product_id.shopinvader_bind_ids").unlink()
        res_line = self._get_line_data()
        self.assertFalse("price" in res_line["product"])
