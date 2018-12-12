# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase
from odoo.addons.sale_promotion_rule.tests.test_promotion import \
    AbstractCommonPromotionCase


class TestCart(CommonConnectedCartCase, AbstractCommonPromotionCase):

    def add_coupon_code(self, coupon_code):
        return self.service.dispatch('update', params={
            'coupon_code': coupon_code,
        })

    def setUp(self, *args, **kwargs):
        self.set_up('shopinvader.sale_order_2')
        super(TestCart, self).setUp(*args, **kwargs)
        self.product_1 = self.env.ref('product.product_product_4b')

    def test_add_coupon(self):
        self.assertFalse(self.cart.has_promotion_rules)
        for line in self.cart.order_line:
            self.assertFalse(line.has_promotion_rules)
        with self.assertRaises(UserError):
            self.add_coupon_code('DGRVBYTHT')

        # if we update the cart, the default rule will be applied to the cart
        res = self.service.dispatch('update', params={})
        for line in self.cart.order_line:
            self.check_discount_rule_set(
                line, self.promotion_rule_auto
            )
        cart = res['store_cache']['cart']
        promotion_rules_auto = cart['promotion_rules_auto']
        promotion_rule_coupon = cart['promotion_rule_coupon']
        self.assertDictEqual({}, promotion_rule_coupon)
        self.assertEquals(1, len(promotion_rules_auto))
        self.assertDictEqual({
            'rule_type': 'auto',
            'discount_type': 'percentage',
            'code': None,
            'name': u'Best Promo Automatic',
            'discount_amount': 10.0}, promotion_rules_auto[0])
        # if coupon the promotion will be recomputed an the new rule will be
        # applied on the SO
        res = self.add_coupon_code(self.promotion_rule_coupon.code)
        for line in self.cart.order_line:
            self.check_discount_rule_set(
                line, self.promotion_rule_coupon
            )
        cart = res['store_cache']['cart']
        promotion_rules_auto = cart['promotion_rules_auto']
        promotion_rule_coupon = cart['promotion_rule_coupon']
        # we see that the auto rule are still applied on the SO event if it's
        # without effect on line since the coupon is the best promotion
        self.assertEquals(1, len(promotion_rules_auto))
        self.assertDictEqual({
            'rule_type': 'coupon',
            'discount_type': 'percentage',
            'code': 'ELDONGHUT',
            'name': u'Best Promo',
            'discount_amount': 20.0}, promotion_rule_coupon)

        # if we remove the coupon, the coupon rule is removed but the default
        # rules are applied
        res = self.service.dispatch('update', params={})
        for line in self.cart.order_line:
            self.check_discount_rule_set(
                line, self.promotion_rule_auto
            )
        cart = res['store_cache']['cart']
        promotion_rules_auto = cart['promotion_rules_auto']
        promotion_rule_coupon = cart['promotion_rule_coupon']
        self.assertDictEqual({}, promotion_rule_coupon)
        self.assertEquals(1, len(promotion_rules_auto))
        self.assertDictEqual({
            'rule_type': 'auto',
            'discount_type': 'percentage',
            'code': None,
            'name': u'Best Promo Automatic',
            'discount_amount': 10.0}, promotion_rules_auto[0])

    def test_promotion_on_item(self):
        self.add_coupon_code(self.promotion_rule_coupon.code)
        count_existing_lines = len(self.cart.order_line)
        # each time we add an item the promotion is recomputed and the coupon
        # code is preserved
        self.service.dispatch('add_item', params={
            'product_id': self.product_1.id,
            'item_qty': 2,
        })
        self.assertEquals(count_existing_lines + 1, len(self.cart.order_line))
        # the promotion is applied on all lines
        for line in self.cart.order_line:
            self.check_discount_rule_set(
                line, self.promotion_rule_coupon
            )
