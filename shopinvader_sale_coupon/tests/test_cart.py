# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.sale_coupon.tests.common import TestSaleCouponCommon
from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class TestCart(CommonConnectedCartCase, TestSaleCouponCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # TODO: This should be in setUpClass, but it has to be
        # changed in shopinvader's CommonConnectedCartCase.
        # Start with an empty cart
        self.cart.order_line.unlink()
        # Config programs
        self.code_promotion_program.reward_type = "discount"

    def _generate_coupons(self, program, qty=1):
        existing_coupons = program.coupon_ids
        # Create coupons
        self.env["coupon.generate.wizard"].with_context(active_id=program.id).create(
            {
                "generation_type": "nbr_coupon",
                "nbr_coupons": qty,
            }
        ).generate_coupon()
        # Return only the created coupons
        return program.coupon_ids - existing_coupons

    def test_immediate_promotion_program(self):
        # Test case 1 (1 A): Assert that no reward is given,
        # as the product B is missing
        res = self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_A.id,
                "item_qty": 1.0,
            },
        )
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promo offer shouldn't have been applied as the product B "
            "isn't in the order",
        )
        self.assertEqual(
            res["data"]["no_code_promo_program_ids"]["count"],
            0,
            "The promo offer shouldn't have been applied as the product B "
            "isn't in the order",
        )
        # Test case 2 (1 A 1 B): Assert that the reward is given,
        # as the product B is now in the order
        res = self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_B.id,
                "item_qty": 1.0,
            },
        )
        self.assertEqual(
            len(self.cart.order_line), 3, "The promo should've been applied"
        )
        self.assertEqual(
            res["data"]["no_code_promo_program_ids"]["count"],
            1,
            "The promo should've been applied",
        )
        self.assertEqual(
            res["data"]["no_code_promo_program_ids"]["items"][0]["id"],
            self.immediate_promotion_program.id,
            "The promo should've been applied",
        )
        # Test case 3 (1 B): Assert that the reward is removed when the order
        # is modified and doesn't match the rules anymore
        res = self.service.dispatch(
            "delete_item",
            params={
                "item_id": self.cart.order_line[0].id,
            },
        )
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promo reward should have been removed as the rules are not "
            "matched anymore",
        )
        self.assertEqual(
            res["data"]["no_code_promo_program_ids"]["count"],
            0,
            "The promo reward should have been removed as the rules are not "
            "matched anymore",
        )
        self.assertEqual(self.cart.order_line.product_id.id, self.product_B.id)

    def test_code_promotion_program(self):
        self.code_promotion_program.promo_code = "promocode"
        # Buy 1 A + Enter code, 1 A is free
        res = self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_A.id,
                "item_qty": 1.0,
            },
        )
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promo offer shouldn't have been applied as the code hasn't "
            "been entered yet",
        )
        self.assertFalse(
            res["data"]["code_promo_program_id"],
            "The promo offer shouldn't have been applied as the code hasn't "
            "been entered yet",
        )
        # Enter an invalid code
        with self.assertRaisesRegex(UserError, "This coupon is invalid"):
            self.service.dispatch("apply_coupon", params={"code": "fakecode"})
        # Enter code
        res = self.service.dispatch("apply_coupon", params={"code": "promocode"})
        self.assertEqual(
            len(self.cart.order_line.ids),
            2,
            "The promo should've been applied",
        )
        self.assertEqual(
            res["data"]["code_promo_program_id"]["id"],
            self.code_promotion_program.id,
            "The promo should've been applied",
        )

    def test_code_promotion_program_coupons(self):
        coupon = self._generate_coupons(self.code_promotion_program)
        # Buy 1 A + Enter code, 1 A is free
        self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_A.id,
                "item_qty": 1.0,
            },
        )
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The coupon shouldn't have been applied as the code hasn't been entered yet",
        )
        # Enter code
        res = self.service.dispatch("apply_coupon", params={"code": coupon.code})
        self.assertEqual(
            len(self.cart.order_line.ids),
            2,
            "The coupon should've been applied",
        )
        self.assertEqual(
            res["data"]["applied_coupon_ids"]["items"][0]["id"],
            coupon.id,
            "The coupon should've been applied",
        )
        self.assertEqual(
            res["data"]["applied_coupon_ids"]["items"][0]["program"]["id"],
            coupon.program_id.id,
            "The coupon should've been applied",
        )
        self.assertEqual(coupon.state, "used")
        # Try to apply twice
        with self.assertRaisesRegex(UserError, "This coupon has already been used"):
            self.service.dispatch("apply_coupon", params={"code": coupon.code})

    def test_promotion_on_next_order(self):
        program = self.env["coupon.program"].create(
            {
                "name": "Free Product A if at least 1 article",
                "promo_code_usage": "no_code_needed",
                "promo_applicability": "on_next_order",
                "program_type": "promotion_program",
                "reward_type": "product",
                "reward_product_id": self.product_A.id,
                "rule_min_quantity": 2,
            }
        )
        # Buy 2 B, 1 A coupon should be given
        res = self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_B.id,
                "item_qty": 2.0,
            },
        )
        generated_coupon = res["data"]["generated_coupon_ids"]["items"][0]
        self.assertEqual(
            generated_coupon["program"]["id"],
            program.id,
            "Coupons for next order should've been generated",
        )
        self.assertEqual(
            generated_coupon["partner"]["id"],
            self.partner.id,
            "Coupons for next order should've been generated for this partner",
        )

    def test_manual_recompute(self):
        # Test case 1 (1 A 1 B): Assert that no reward is given because
        # we're skipping the recompute
        self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_A.id,
                "item_qty": 1.0,
                "skip_coupon_recompute": True,
            },
        )
        self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_B.id,
                "item_qty": 1.0,
                "skip_coupon_recompute": True,
            },
        )
        self.assertEqual(
            len(self.cart.order_line),
            2,
            "The promo shouldn't have been applied as we're skipping recompute",
        )
        self.service.dispatch("recompute_coupon_lines")
        self.assertEqual(
            len(self.cart.order_line), 3, "The promo should've been applied"
        )
