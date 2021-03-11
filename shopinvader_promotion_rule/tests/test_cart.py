# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.sale_promotion_rule.tests.test_promotion import (
    AbstractCommonPromotionCase,
)
from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase
from odoo.exceptions import UserError


class TestCart(CommonConnectedCartCase, AbstractCommonPromotionCase):
    def add_coupon_code(self, coupon_code):
        return self.service.dispatch(
            "update", params={"coupon_code": coupon_code}
        )

    def setUp(self, *args, **kwargs):
        super(TestCart, self).setUp(*args, **kwargs)
        self.set_up("shopinvader.sale_order_2")
        self.product_1 = self.env.ref("product.product_product_4b")

    def test_add_coupon(self):
        self.assertFalse(self.cart.has_promotion_rules)
        for line in self.cart.order_line:
            self.assertFalse(line.has_promotion_rules)
        with self.assertRaises(UserError):
            self.add_coupon_code("DGRVBYTHT")

        # if we update the cart, the default rule will be applied to the cart
        res = self.service.dispatch("update", params={})
        for line in self.cart.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_auto)
        cart = res["store_cache"]["cart"]
        promotion_rules_auto = cart["promotion_rules_auto"]
        promotion_rule_coupon = cart["promotion_rule_coupon"]
        self.assertDictEqual({}, promotion_rule_coupon)
        self.assertEquals(1, len(promotion_rules_auto))
        self.assertDictEqual(
            {
                "rule_type": "auto",
                "discount_type": "percentage",
                "code": None,
                "name": u"Best Promo Automatic",
                "discount_amount": 10.0,
            },
            promotion_rules_auto[0],
        )
        # if coupon the promotion will be recomputed an the new rule will be
        # applied on the SO
        res = self.add_coupon_code(self.promotion_rule_coupon.code)
        for line in self.cart.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_coupon)
        cart = res["store_cache"]["cart"]
        promotion_rules_auto = cart["promotion_rules_auto"]
        promotion_rule_coupon = cart["promotion_rule_coupon"]
        # we see that the auto rule are still applied on the SO event if it's
        # without effect on line since the coupon is the best promotion
        self.assertEquals(1, len(promotion_rules_auto))
        self.assertDictEqual(
            {
                "rule_type": "coupon",
                "discount_type": "percentage",
                "code": "ELDONGHUT",
                "name": u"Best Promo",
                "discount_amount": 20.0,
            },
            promotion_rule_coupon,
        )
        # if we update the cart without specifying a coupon into the message
        # the coupon is preserved
        res = self.service.dispatch("update", params={})
        for line in self.cart.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_coupon)

        # if we update the cart with an empty coupon,
        # the coupon rule is removed but the default
        # rules are applied
        res = self.service.dispatch("update", params={"coupon_code": None})
        for line in self.cart.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_auto)
        cart = res["store_cache"]["cart"]
        promotion_rules_auto = cart["promotion_rules_auto"]
        promotion_rule_coupon = cart["promotion_rule_coupon"]
        self.assertDictEqual({}, promotion_rule_coupon)
        self.assertEquals(1, len(promotion_rules_auto))
        self.assertDictEqual(
            {
                "rule_type": "auto",
                "discount_type": "percentage",
                "code": None,
                "name": u"Best Promo Automatic",
                "discount_amount": 10.0,
            },
            promotion_rules_auto[0],
        )

    def test_promotion_on_item(self):
        self.add_coupon_code(self.promotion_rule_coupon.code)
        count_existing_lines = len(self.cart.order_line)
        # each time we add an item the promotion is recomputed and the coupon
        # code is preserved
        self.service.dispatch(
            "add_item", params={"product_id": self.product_1.id, "item_qty": 2}
        )
        self.assertEquals(count_existing_lines + 1, len(self.cart.order_line))
        # the promotion is applied on all lines
        for line in self.cart.order_line:
            self.check_discount_rule_set(line, self.promotion_rule_coupon)

    def test_promotion_on_item_simple(self):
        self.backend.simple_cart_service = True
        self.add_coupon_code(self.promotion_rule_coupon.code)
        count_existing_lines = len(self.cart.order_line)
        old_lines = self.cart.order_line
        # each time we add an item the promotion is recomputed and the coupon
        # code is preserved
        self.service.dispatch(
            "add_item", params={"product_id": self.product_1.id, "item_qty": 2}
        )
        self.assertEquals(count_existing_lines + 1, len(self.cart.order_line))
        new_line = self.cart.order_line - old_lines
        self.assertFalse(new_line.coupon_promotion_rule_id)
        cart_data = self.service.dispatch("search")["data"]
        cart = self.env["sale.order"].browse(cart_data["id"])
        new_line = cart.order_line - old_lines
        # As a search has been done, the cart computation has been forced
        self.check_discount_rule_set(new_line, self.promotion_rule_coupon)
        # the promotion is applied on all lines
        for line in self.cart.order_line - new_line:
            self.check_discount_rule_set(line, self.promotion_rule_coupon)

    def _sign_with(self, partner):
        """
        Simulate a sign_in with the given partner
        :param partner: res.partner recordset
        :return:
        """
        self.service.work.partner = partner
        service_sign = self.service.component("customer")
        service_sign.sign_in()

    def test_promotion_rule_applied_after_fiscal_pos_update(self):
        """
        Ensure promotions are correctly applied even after updating the
        fiscal position using the write_with_onchange (on cart).
        :return:
        """
        fiscal_position = self.env.ref("shopinvader.fiscal_position_0")
        # Apply promo rule
        self.cart.apply_promotions()
        # Then ensure a promo should be applied
        self.assertIn(self.promotion_rule_auto, self.cart.promotion_rule_ids)
        save_price_with_promo = self.cart.amount_total
        # Clear promo to ensure they will be automatically set later
        self.cart.clear_promotions()
        self.assertFalse(self.cart.promotion_rule_ids)
        self.assertFalse(self.cart.fiscal_position_id)
        # Now add manually promotions
        self.cart.write(
            {"promotion_rule_ids": [(4, self.promotion_rule_auto.id, False)]}
        )
        # Update the fiscal position to have reset_price
        # set to True (cfr shopinvader module)
        self.cart.write_with_onchange(
            {"fiscal_position_id": fiscal_position.id}
        )
        self.assertAlmostEquals(
            self.cart.amount_total,
            save_price_with_promo,
            places=self.price_precision_digits,
        )

    def test_promotion_rule_backend_enable(self):
        """
        Ensure the _check_valid_shopinvader_backend return the correct value.
        If promo rules on the backend are not disabled, the result of this
        function should be True (this case).
        :return:
        """
        self.assertFalse(
            self.promotion_rule_auto.restriction_shopinvader_backend_ids
        )
        self.assertTrue(
            self.promotion_rule_auto._check_valid_shopinvader_backend(
                self.cart
            )
        )
        self.assertIn(
            "shopinvader_backend", self.promotion_rule_auto._get_restrictions()
        )

    def test_promotion_rule_backend_disabled(self):
        """
        Ensure the _check_valid_shopinvader_backend return the correct value.
        If promo rules on the backend are disabled, the result of this
        function should be False (this case).
        :return:
        """
        self.promotion_rule_auto.write(
            {
                "restriction_shopinvader_backend_ids": [
                    (6, False, self.cart.shopinvader_backend_id.ids)
                ]
            }
        )

        self.assertFalse(
            self.promotion_rule_auto._check_valid_shopinvader_backend(
                self.cart
            )
        )
