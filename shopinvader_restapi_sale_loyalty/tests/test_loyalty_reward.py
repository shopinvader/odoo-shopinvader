# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.sale_loyalty.tests.common import TestSaleCouponCommon

from .common import TestShopinvaderSaleLoyaltyCommon


class TestLoyaltyReward(TestSaleCouponCommon, TestShopinvaderSaleLoyaltyCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="reward")

    def test_code_promotion_program_reward(self):
        """
        Generate coupons for code_promotion_program and check get_rewards
        service.
        """
        coupon = self._generate_coupons(self.code_promotion_program)
        res = self.service.dispatch(
            "get_rewards",
            params={
                "code": coupon.code,
            },
        )
        self.assertEqual(len(res), 1)
        reward = res[0]
        self.assertEqual(reward["reward_type"], "product")
        self.assertEqual(reward["reward_products"], [{"id": self.product_A.id}])

    def test_code_choice_reward(self):
        program = self._create_program_choice_reward(self.product_A)
        coupon = self._generate_coupons(program)
        res = self.service.dispatch(
            "get_rewards",
            params={
                "code": coupon.code,
            },
        )
        self.assertEqual(len(res), 2)
        first_reward = res[0]
        second_reward = res[1]
        self.assertEqual(first_reward["reward_type"], "discount")
        self.assertEqual(first_reward["discount"], 10)
        self.assertEqual(first_reward["discount_mode"], "percent")
        self.assertEqual(first_reward["discount_applicability"], "order")
        self.assertEqual(second_reward["reward_type"], "discount")
        self.assertEqual(second_reward["discount"], 25)
        self.assertEqual(second_reward["discount_mode"], "percent")
        self.assertEqual(second_reward["discount_applicability"], "cheapest")

    def test_free_product_choice(self):
        self.product_B.product_tag_ids = [(4, self.gift_product_tag.id)]
        self.product_C.product_tag_ids = [(4, self.gift_product_tag.id)]
        program = self._create_program_free_product_choice(
            self.product_A, self.gift_product_tag
        )
        coupon = self._generate_coupons(program)
        res = self.service.dispatch(
            "get_rewards",
            params={
                "code": coupon.code,
            },
        )
        self.assertEqual(len(res), 1)
        reward = res[0]
        self.assertEqual(reward["reward_type"], "product")
        self.assertEqual(len(reward["reward_products"]), 2)
        self.assertIn({"id": self.product_B.id}, reward["reward_products"])
        self.assertIn({"id": self.product_C.id}, reward["reward_products"])

    def test_code_on_rule(self):
        self._create_discount_code_program()
        res = self.service.dispatch(
            "get_rewards",
            params={
                "code": "PROMOTION",
            },
        )
        self.assertEqual(len(res), 1)
        reward = res[0]
        self.assertEqual(reward["reward_type"], "discount")
        self.assertEqual(reward["discount"], 50)
        self.assertEqual(reward["discount_mode"], "percent")
        self.assertEqual(reward["discount_applicability"], "order")

    def test_wrong_code(self):
        res = self.service.dispatch(
            "get_rewards",
            params={
                "code": "wrong_code",
            },
        )
        self.assertEqual(len(res), 0)
