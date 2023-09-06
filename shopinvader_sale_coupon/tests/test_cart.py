# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.sale_loyalty.tests.common import TestSaleCouponCommon
from odoo.addons.shopinvader_restapi.tests.test_cart import CommonConnectedCartCase


class TestCart(CommonConnectedCartCase, TestSaleCouponCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # Start with an empty cart
        self.cart.order_line.unlink()
        # Archive immediate promotion program or it will be applied everywhere
        self.immediate_promotion_program.active = False

    def _generate_coupons(self, program, qty=1):
        existing_coupons = program.coupon_ids
        # Create coupons
        self.env["loyalty.generate.wizard"].with_context(active_id=program.id).create(
            {
                "coupon_qty": qty,
            }
        ).generate_coupons()
        # Return only the created coupons
        return program.coupon_ids - existing_coupons

    def _create_promotion_program_A_B(self):

        # Configure a new promotion program: when 1A and 1B are in the cart,
        # 1B becomes free (100% discount on it)
        return self.env["loyalty.program"].create(
            {
                "name": "Add  1A + 1 B in cart, 1B becomes free",
                "program_type": "promotion",
                "applies_on": "current",
                "company_id": self.env.company.id,
                "trigger": "auto",
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "product_ids": self.product_A,
                            "reward_point_amount": 1,
                            "reward_point_mode": "order",
                            "minimum_qty": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_ids": self.product_B,
                            "reward_point_amount": 1,
                            "reward_point_mode": "order",
                            "minimum_qty": 1,
                        },
                    ),
                ],
                "reward_ids": [
                    (
                        0,
                        0,
                        {
                            "reward_type": "discount",
                            "discount": 100,
                            "discount_applicability": "specific",
                            "discount_product_ids": [(4, self.product_B.id)],
                            "required_points": 2,
                        },
                    )
                ],
            }
        )

    def test_immediate_promotion_program(self):
        """
        With immediate promotion program, as soon as 1A is added
        in cart, 1B is automatically added and free.
        """
        # Unarchive immediate promotion program for this specific case
        self.immediate_promotion_program.active = True
        # Test case 1 (1 A): Assert that reward is given
        res = self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_A.id,
                "item_qty": 1.0,
            },
        )
        self.assertEqual(
            len(self.cart.order_line),
            2,
            "The promo offer should have been automatically applied",
        )
        self.assertEqual(
            res["data"]["no_code_promo_program_ids"]["count"],
            1,
            "The promo offer should have been automatically applied",
        )
        # Test case 2 (- 1A): Assert that the reward is removed when the order
        # is modified and doesn't match the rules anymore
        res = self.service.dispatch(
            "delete_item",
            params={
                "item_id": self.cart.order_line[0].id,
            },
        )
        self.assertEqual(
            len(self.cart.order_line),
            0,
            "The promo reward should have been removed as the rules are not "
            "matched anymore",
        )
        self.assertEqual(
            res["data"]["no_code_promo_program_ids"]["count"],
            0,
            "The promo reward should have been removed as the rules are not "
            "matched anymore",
        )

    def test_promotion_program(self):
        promotion_program = self._create_promotion_program_A_B()

        # Test case 1 (+ 1 A): Assert that no reward is given,
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
        # Test case 2 (+ 1 B): Assert that the reward is given,
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
            promotion_program.id,
            "The promo should've been applied",
        )
        # Test case 3 (-1 A): Assert that the reward is removed when the order
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
        promo_code = self.code_promotion_program_with_discount.rule_ids[0].code
        # Buy 1 C + Enter code, 10% discount on C
        res = self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_C.id,
                "item_qty": 1.0,
            },
        )
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promo offer shouldn't have been applied as the code hasn't "
            "been entered yet",
        )
        self.assertEqual(
            res["data"]["code_promo_program_ids"]["count"],
            0,
            "The promo offer shouldn't have been applied as the code hasn't "
            "been entered yet",
        )
        # Enter an invalid code
        with self.assertRaisesRegex(UserError, r"This code is invalid \(fakecode\)\."):
            self.service.dispatch("apply_coupon", params={"code": "fakecode"})
        # Enter code
        res = self.service.dispatch("apply_coupon", params={"code": promo_code})
        self.assertEqual(
            len(self.cart.order_line.ids),
            2,
            "The promo should've been applied",
        )
        self.assertEqual(
            res["data"]["code_promo_program_ids"]["items"][0]["id"],
            self.code_promotion_program_with_discount.id,
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
        # Try to apply twice
        with self.assertRaisesRegex(
            UserError, "This program is already applied to this order."
        ):
            self.service.dispatch("apply_coupon", params={"code": coupon.code})

    def test_promotion_on_next_order(self):
        program = self.env["loyalty.program"].create(
            {
                "name": "Free Product A if at least 2 articles",
                "program_type": "next_order_coupons",
                "trigger": "auto",
                "applies_on": "future",
                "company_id": self.env.company.id,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "reward_point_amount": 1,
                            "reward_point_mode": "order",
                            "minimum_qty": 2,
                        },
                    )
                ],
                "reward_ids": [
                    (
                        0,
                        0,
                        {
                            "reward_type": "product",
                            "reward_product_id": self.product_A.id,
                            "reward_product_qty": 1,
                            "required_points": 1,
                        },
                    )
                ],
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

    def test_reward_amount(self):
        cart = self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_A.id,
                "item_qty": 1.0,
            },
        )
        # FIXME: compute_reward_total changed: in v14 all lines had a price,
        # and for tax included products, the amount on the SO was the price
        # tax excluded.
        # Here in v16 the price on the line is 0 (as the product is free),
        # and the compute goes on the product to take the lst_price.
        # But for tax included products, the lst_price includes the tax...
        # To sum up, reward_amount sometimes contains the tax (for tax
        # included products) and otherwise not...
        self.assertAlmostEqual(
            cart["data"]["reward_amount"],
            -self.product_B.taxes_id.compute_all(self.product_B.list_price)[
                "total_excluded"
            ],
            2,
            "Untaxed reward amount should be untaxed unit price of product B",
        )
        self.assertAlmostEqual(
            cart["data"]["reward_amount_tax_incl"],
            -self.product_B.list_price,
            2,
            "Tax included reward amount should be tax included unit price of product B",
        )

    def test_manual_recompute(self):
        # Test case 1 (1 A + 1 B in cart -> 1B becomes free):
        # Assert that no reward is given when we're skipping the recompute
        self._create_promotion_program_A_B()
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

    def test_reward_choice(self):
        """
        Create a new program with code that gives you the choice: if A is bought,
        either you get 10% on all or 25% on the cheapest article.

        -> when adding coupon code, if reward is not specified, an error is
        raised.
        """
        program = self.env["loyalty.program"].create(
            {
                "name": "Buy 1A, choose 10% on all or 25% on cheapest",
                "program_type": "coupons",
                "trigger": "with_code",
                "applies_on": "current",
                "company_id": self.env.company.id,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "product_ids": [(4, self.product_A.id)],
                            "minimum_qty": 1,
                        },
                    )
                ],
                "reward_ids": [
                    (
                        0,
                        0,
                        {
                            "reward_type": "discount",
                            "discount": 10,
                            "required_points": 1,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "reward_type": "discount",
                            "discount": 25,
                            "discount_applicability": "cheapest",
                            "required_points": 1,
                        },
                    ),
                ],
            }
        )
        coupon = self._generate_coupons(program)
        self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_A.id,
                "item_qty": 1.0,
            },
        )
        with self.assertRaisesRegex(
            UserError, "Several rewards available. Please specify one."
        ):
            self.service.dispatch("apply_coupon", params={"code": coupon.code})

        allowed_rewards = program.reward_ids
        wrong_reward = self.env["loyalty.reward"].search(
            [("id", "not in", allowed_rewards.ids)], limit=1
        )

        with self.assertRaisesRegex(UserError, "Reward not allowed for this code."):
            self.service.dispatch(
                "apply_coupon",
                params={"code": coupon.code, "reward_id": wrong_reward.id},
            )

        self.service.dispatch(
            "apply_coupon",
            params={"code": coupon.code, "reward_id": program.reward_ids[0].id},
        )
        self.assertEqual(
            len(self.cart.order_line), 2, "The reward should've been applied"
        )
        self.assertEqual(
            self.cart._get_reward_lines().product_id.name, "10% on your order"
        )

    def test_product_choice(self):
        """
        Create a new program with code that gives you the choice: if A is bought,
        either you get product_B for free, or product_C for free

        -> when adding coupon code, if product is not specified, an error is
        raised.
        """
        product_tag = self.env["product.tag"].create({"name": "Gift Product"})
        self.product_B.product_tag_ids = [(4, product_tag.id)]
        self.product_C.product_tag_ids = [(4, product_tag.id)]
        program = self.env["loyalty.program"].create(
            {
                "name": "Choice 1B or 1C free if 1A bought",
                "program_type": "coupons",
                "trigger": "with_code",
                "applies_on": "current",
                "company_id": self.env.company.id,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "product_ids": [(4, self.product_A.id)],
                            "minimum_qty": 1,
                        },
                    )
                ],
                "reward_ids": [
                    (
                        0,
                        0,
                        {
                            "reward_type": "product",
                            "reward_product_tag_id": product_tag.id,
                        },
                    )
                ],
            }
        )
        coupon = self._generate_coupons(program)
        self.service.dispatch(
            "add_item",
            params={
                "product_id": self.product_A.id,
                "item_qty": 1.0,
            },
        )
        with self.assertRaisesRegex(
            UserError, "Several free products available. Please specify one."
        ):
            self.service.dispatch("apply_coupon", params={"code": coupon.code})

        allowed_products = program.reward_ids[0].reward_product_ids
        wrong_product = self.env["product.product"].search(
            [("id", "not in", allowed_products.ids)], limit=1
        )

        with self.assertRaisesRegex(
            UserError, "Free product not allowed for this reward."
        ):
            self.service.dispatch(
                "apply_coupon",
                params={"code": coupon.code, "free_product_id": wrong_product.id},
            )

        self.service.dispatch(
            "apply_coupon",
            params={
                "code": coupon.code,
                "free_product_id": allowed_products[0].id,
            },
        )
        self.assertEqual(
            len(self.cart.order_line), 2, "The reward should've been applied"
        )
        self.assertEqual(self.cart._get_reward_lines().product_id, self.product_B)
