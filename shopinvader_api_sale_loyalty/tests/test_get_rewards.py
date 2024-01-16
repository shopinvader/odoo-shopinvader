# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from fastapi import status
from requests import Response

from odoo.tests.common import tagged

from ..routers.loyalty import loyalty_router
from .common import TestShopinvaderSaleLoyaltyCommon


@tagged("post_install", "-at_install")
class TestLoyaltyReward(TestShopinvaderSaleLoyaltyCommon):
    def test_reward_wrong_code(self) -> None:
        with self._create_test_client(router=loyalty_router) as test_client:
            response: Response = test_client.get("/loyalty/wrongcode")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_deprecated_route_rewards(self) -> None:
        """
        Check that deprecated route /rewards/{code} is still reachable.
        """
        with self._create_test_client(router=loyalty_router) as test_client:
            response: Response = test_client.get("/rewards/wrongcode")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_code_promotion_program_reward(self):
        """
        Generate coupons for code_promotion_program and check get_rewards
        service.
        """
        coupon = self._generate_coupons(self.code_promotion_program)
        with self._create_test_client(router=loyalty_router) as test_client:
            response: Response = test_client.get(f"/loyalty/{coupon.code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(len(res), 1)
        reward = res[0]
        self.assertEqual(reward["reward_type"], "product")
        self.assertEqual(reward["reward_product_ids"], [self.product_A.id])

    def test_code_choice_reward(self):
        program = self._create_program_choice_reward_with_code(self.product_A)
        coupon = self._generate_coupons(program)
        with self._create_test_client(router=loyalty_router) as test_client:
            response: Response = test_client.get(f"/loyalty/{coupon.code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
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
        program = self._create_program_free_product_choice_with_code(
            self.product_A, self.gift_product_tag
        )
        coupon = self._generate_coupons(program)
        with self._create_test_client(router=loyalty_router) as test_client:
            response: Response = test_client.get(f"/loyalty/{coupon.code}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(len(res), 1)
        reward = res[0]
        self.assertEqual(reward["reward_type"], "product")
        self.assertEqual(len(reward["reward_product_ids"]), 2)
        self.assertEqual(
            set(reward["reward_product_ids"]), {self.product_B.id, self.product_C.id}
        )

    def test_code_on_rule(self):
        self._create_discount_code_program()
        with self._create_test_client(router=loyalty_router) as test_client:
            response: Response = test_client.get("/loyalty/PROMOTION")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.json()
        self.assertEqual(len(res), 1)
        reward = res[0]
        self.assertEqual(reward["reward_type"], "discount")
        self.assertEqual(reward["discount"], 50)
        self.assertEqual(reward["discount_mode"], "percent")
        self.assertEqual(reward["discount_applicability"], "order")
