# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import uuid

from requests import Response

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from odoo.addons.shopinvader_api_cart.routers import cart_router

from .common import TestShopinvaderSaleLoyaltyCommon


@tagged("post_install", "-at_install")
class TestLoyaltyCard(TestShopinvaderSaleLoyaltyCommon):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_with_rights.groups_id = [
            (
                6,
                0,
                [
                    cls.env.ref(
                        "shopinvader_api_security_sale.shopinvader_sale_user_group"
                    ).id,
                ],
            )
        ]
        # Archive immediate promotion program or it will be applied everywhere
        cls.immediate_promotion_program.active = False
        cls.cart = cls.env["sale.order"]._create_empty_cart(
            cls.default_fastapi_authenticated_partner.id
        )
        cls.dummy_uuid = str(uuid.uuid4())

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
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line),
            2,
            "The promo offer should have been automatically applied",
        )
        self.assertEqual(
            len(res["programs"]),
            1,
            "The promo offer should have been automatically applied",
        )
        # # Test case 2 (- 1A): Assert that the reward is removed when the order
        # # is modified and doesn't match the rules anymore
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {
                        "uuid": self.dummy_uuid,
                        "product_id": self.product_A.id,
                        "qty": -1,
                    }
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line),
            0,
            "The promo reward should have been removed as the rules are not "
            "matched anymore",
        )
        self.assertEqual(
            res["programs"],
            [],
            "The promo reward should have been removed as the rules are not "
            "matched anymore",
        )

    def test_promotion_program(self):
        promotion_program = self._create_promotion_program_A_B()

        # Test case 1 (+ 1 A): Assert that no reward is given,
        # as the product B is missing
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promo offer shouldn't have been applied as the product B "
            "isn't in the order",
        )
        self.assertEqual(
            res["programs"],
            [],
            "The promo offer shouldn't have been applied as the product B "
            "isn't in the order",
        )
        # Test case 2 (+ 1 B): Assert that the reward is given,
        # as the product B is now in the order
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_B.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line), 3, "The promo should've been applied"
        )
        self.assertEqual(
            len(res["programs"]),
            1,
            "The promo should've been applied",
        )
        self.assertEqual(
            res["programs"][0]["id"],
            promotion_program.id,
            "The promo should've been applied",
        )
        # Test case 3 (-1 A): Assert that the reward is removed when the order
        # is modified and doesn't match the rules anymore
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {
                        "uuid": self.dummy_uuid,
                        "product_id": self.product_A.id,
                        "qty": -1,
                    }
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promo reward should have been removed as the rules are not "
            "matched anymore",
        )
        self.assertEqual(
            res["programs"],
            [],
            "The promo reward should have been removed as the rules are not "
            "matched anymore",
        )
        self.assertEqual(self.cart.order_line.product_id.id, self.product_B.id)

    def test_code_promotion_program(self):
        promo_code = self.code_promotion_program_with_discount.rule_ids[0].code
        # Buy 1 C + Enter code, 10% discount on C
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_C.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promo offer shouldn't have been applied as the code hasn't "
            "been entered yet",
        )
        self.assertEqual(
            res["programs"],
            [],
            "The promo offer shouldn't have been applied as the code hasn't "
            "been entered yet",
        )
        # Enter an invalid code
        with self._create_test_client(
            router=cart_router
        ) as test_client, self.assertRaisesRegex(
            UserError, r"This code is invalid \(fakecode\)\."
        ):
            data = {"code": "fakecode"}
            test_client.post("/coupon", content=json.dumps(data))
        # Enter code
        with self._create_test_client(router=cart_router) as test_client:
            data = {"code": promo_code}
            response = test_client.post("/coupon", content=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line.ids),
            2,
            "The promo should've been applied",
        )
        self.assertEqual(
            res["programs"][0]["id"],
            self.code_promotion_program_with_discount.id,
            "The promo should've been applied",
        )

    def test_route_current_coupon(self):
        """
        Test that the route /current/coupon is reachable
        """
        # Buy 1 C + Enter code, 10% discount on C
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {
                        "uuid": self.dummy_uuid,
                        "product_id": self.product_C.id,
                        "qty": 1,
                    }
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promo offer shouldn't have been applied as the code hasn't "
            "been entered yet",
        )
        self.assertEqual(
            res["programs"],
            [],
            "The promo offer shouldn't have been applied as the code hasn't "
            "been entered yet",
        )
        # Enter an invalid code
        with self._create_test_client(
            router=cart_router
        ) as test_client, self.assertRaisesRegex(
            UserError, r"This code is invalid \(fakecode\)\."
        ):
            data = {"code": "fakecode"}
            test_client.post("/current/coupon", content=json.dumps(data))

    def test_deprecated_route_apply_coupon(self):
        """
        Test that the deprecated route /apply_coupon is still reachable.
        :return:
        """
        # Enter an invalid code
        with self._create_test_client(
            router=cart_router
        ) as test_client, self.assertRaisesRegex(
            UserError, r"This code is invalid \(fakecode\)\."
        ):
            data = {"code": "fakecode"}
            test_client.post("/apply_coupon", content=json.dumps(data))

    def test_code_promotion_program_coupons(self):
        coupon = self._generate_coupons(self.code_promotion_program)
        # Buy 1 A + Enter code, 1 A is free
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The coupon shouldn't have been applied as the code hasn't been entered yet",
        )
        # Enter code
        with self._create_test_client(router=cart_router) as test_client:
            data = {"code": coupon.code}
            response = test_client.post("/coupon", content=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line.ids),
            2,
            "The coupon should've been applied",
        )
        self.assertEqual(res["promo_codes"], [coupon.code])
        # Try to apply twice
        with self._create_test_client(
            router=cart_router
        ) as test_client, self.assertRaisesRegex(
            UserError, "This program is already applied to this order."
        ):
            data = {"code": coupon.code}
            test_client.post("/coupon", content=json.dumps(data))

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
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_B.id, "qty": 2}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        res = response.json()
        generated_coupons = res["generated_coupons"]
        self.assertEqual(len(generated_coupons), 1)
        self.assertEqual(
            generated_coupons[0]["program"]["id"],
            program.id,
            "Coupons for next order should've been generated",
        )

    def test_reward_amount_discount(self):
        self._create_discount_code_program()
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            test_client.post("/sync", content=json.dumps(data))
        with self._create_test_client(router=cart_router) as test_client:
            data = {"code": "PROMOTION"}
            response: Response = test_client.post("/coupon", content=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        cart = response.json()
        self.assertAlmostEqual(
            cart["reward_amount"],
            -0.5
            * self.product_A.taxes_id.compute_all(self.product_A.lst_price)[
                "total_excluded"
            ],
            2,
            "Untaxed reward amount should be 50% of untaxed unit price of product A",
        )
        self.assertAlmostEqual(
            cart["reward_amount_tax_incl"],
            -0.5
            * self.product_A.taxes_id.compute_all(self.product_A.lst_price)[
                "total_included"
            ],
            2,
            "Tax included reward amount should be 50% of tax included unit price of product A",
        )

    def test_reward_amount_free_product(self):
        self.immediate_promotion_program.active = True
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        cart = response.json()
        self.assertAlmostEqual(
            cart["reward_amount"],
            -self.product_B.taxes_id.compute_all(self.product_B.lst_price)[
                "total_excluded"
            ],
            2,
            "Untaxed reward amount should be untaxed unit price of product B",
        )
        self.assertAlmostEqual(
            cart["reward_amount_tax_incl"],
            -self.product_B.taxes_id.compute_all(self.product_B.lst_price)[
                "total_included"
            ],
            2,
            "Tax included reward amount should be tax included unit price of product B",
        )

    def test_program_with_code_reward_choice(self):
        """
        Create a new program with code that gives you the choice: if A is bought,
        either you get 10% on all or 25% on the cheapest article.

        -> when adding coupon code, if reward is not specified, an error is
        raised.
        """
        program = self._create_program_choice_reward_with_code(self.product_A)
        coupon = self._generate_coupons(program)
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        with self._create_test_client(
            router=cart_router
        ) as test_client, self.assertRaisesRegex(
            UserError, "Several rewards available. Please specify one."
        ):
            data = {"code": coupon.code}
            test_client.post("/coupon", content=json.dumps(data))
        allowed_rewards = program.reward_ids
        wrong_reward = self.env["loyalty.reward"].search(
            [("id", "not in", allowed_rewards.ids)], limit=1
        )
        with self._create_test_client(
            router=cart_router
        ) as test_client, self.assertRaisesRegex(
            UserError, "Reward not allowed for this code."
        ):
            data = {"code": coupon.code, "reward_id": wrong_reward.id}
            test_client.post("/coupon", content=json.dumps(data))

        with self._create_test_client(router=cart_router) as test_client:
            data = {"code": coupon.code, "reward_id": program.reward_ids[0].id}
            response = test_client.post("/coupon", content=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(self.cart.order_line), 2, "The reward should've been applied"
        )
        self.assertEqual(
            self.cart._get_reward_lines().product_id.name, "10% on your order"
        )

    def test_program_auto_reward_choice(self):
        """
        Create a new program (automatic) that gives you the choice: if A is bought,
        either you get 10% on all or 25% on the cheapest article.

        -> when updating the cart, the reward is not automatically applied
        as there are several rewards linked to the program.
        But the rewards are in the Sale Pydantic model, under claimable_rewards

        Then calling /reward applies the reward and removes the rewards
        from the Sale Pydantic model
        """
        program = self._create_program_choice_reward_auto(self.product_A)
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promotion shouldn't be applied as there is a reward choice",
        )
        res = response.json()
        claimable_rewards = res["claimable_rewards"]
        self.assertEqual(
            len(claimable_rewards), 2, "The two possible rewards should be claimable."
        )
        self.assertEqual(
            {claimable_rewards[0]["id"], claimable_rewards[1]["id"]},
            set(program.reward_ids.ids),
        )

        # Apply the reward
        with self._create_test_client(router=cart_router) as test_client:
            data = {"reward_id": claimable_rewards[0]["id"]}
            response: Response = test_client.post("/reward", content=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line),
            2,
            "The promotion should have been applied",
        )
        self.assertEqual(
            res["claimable_rewards"], [], "Rewards shouldn't be claimable anymore"
        )

    def test_program_with_code_product_choice(self):
        """
        Create a new program with code that gives you the choice: if A is bought,
        either you get product_B for free, or product_C for free

        -> when adding coupon code, if product is not specified, an error is
        raised.
        """
        self.product_B.product_tag_ids = [(4, self.gift_product_tag.id)]
        self.product_C.product_tag_ids = [(4, self.gift_product_tag.id)]
        program = self._create_program_free_product_choice_with_code(
            self.product_A, self.gift_product_tag
        )
        coupon = self._generate_coupons(program)
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            test_client.post("/sync", content=json.dumps(data))
        with self._create_test_client(
            router=cart_router
        ) as test_client, self.assertRaisesRegex(
            UserError, "Several free products available. Please specify one."
        ):
            data = {"code": coupon.code}
            test_client.post("/coupon", content=json.dumps(data))
        allowed_products = program.reward_ids[0].reward_product_ids
        wrong_product = self.env["product.product"].search(
            [("id", "not in", allowed_products.ids)], limit=1
        )

        with self._create_test_client(
            router=cart_router
        ) as test_client, self.assertRaisesRegex(
            UserError, "Free product not allowed for this reward."
        ):
            data = {"code": coupon.code, "free_product_id": wrong_product.id}
            test_client.post("/coupon", content=json.dumps(data))

        with self._create_test_client(router=cart_router) as test_client:
            data = {"code": coupon.code, "free_product_id": allowed_products[0].id}
            response = test_client.post("/coupon", content=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(self.cart.order_line), 2, "The reward should've been applied"
        )
        self.assertEqual(self.cart._get_reward_lines().product_id, self.product_B)

    def test_program_auto_product_choice(self):
        """
        Create a new program (automatic) that gives you the choice
        between several free products

        -> when updating the cart, the reward is not automatically applied
        as there is a choice to make.

        When calling /reward without specified product, the service fails.
        When specifying the product, the reward is added.
        """
        self.product_B.product_tag_ids = [(4, self.gift_product_tag.id)]
        self.product_C.product_tag_ids = [(4, self.gift_product_tag.id)]
        program = self._create_program_free_product_choice_auto(
            self.product_A, self.gift_product_tag
        )
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promotion shouldn't be applied as there is a reward choice",
        )
        res = response.json()
        claimable_rewards = res["claimable_rewards"]
        self.assertEqual(
            len(claimable_rewards), 1, "There is only 1 possible claimable reward."
        )
        self.assertEqual(claimable_rewards[0]["id"], program.reward_ids.id)
        self.assertEqual(
            set(claimable_rewards[0]["reward_product_ids"]),
            set(self.gift_product_tag.product_ids.ids),
            "There should be a choice between 2 claimable free products.",
        )

        # Try applying reward without specifying the product
        with self._create_test_client(
            router=cart_router
        ) as test_client, self.assertRaisesRegex(
            UserError, "Several free products available. Please specify one."
        ):
            data = {"reward_id": claimable_rewards[0]["id"]}
            test_client.post("/reward", content=json.dumps(data))

        # Apply the reward specifying the product
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "reward_id": claimable_rewards[0]["id"],
                "free_product_id": self.product_C.id,
            }
            response = test_client.post("/reward", content=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(
            len(self.cart.order_line),
            2,
            "The promotion should have been applied",
        )
        self.assertEqual(res["claimable_rewards"], [])

    def test_route_current_reward(self):
        """
        Check that route /current/reward is reachable.
        """
        program = self._create_program_choice_reward_auto(self.product_A)
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promotion shouldn't be applied as there is a reward choice",
        )
        res = response.json()
        claimable_rewards = res["claimable_rewards"]
        self.assertEqual(
            len(claimable_rewards), 2, "The two possible rewards should be claimable."
        )
        self.assertEqual(
            {claimable_rewards[0]["id"], claimable_rewards[1]["id"]},
            set(program.reward_ids.ids),
        )
        with self._create_test_client(router=cart_router) as test_client:
            data = {"reward_id": claimable_rewards[0]["id"]}
            response: Response = test_client.post(
                "/current/reward", content=json.dumps(data)
            )
        self.assertEqual(response.status_code, 200)

    def test_deprecated_route_apply_reward(self):
        """
        Check that deprecated route /apply_reward is still reachable.
        """
        program = self._create_program_choice_reward_auto(self.product_A)
        with self._create_test_client(router=cart_router) as test_client:
            data = {
                "transactions": [
                    {"uuid": self.dummy_uuid, "product_id": self.product_A.id, "qty": 1}
                ]
            }
            response: Response = test_client.post("/sync", content=json.dumps(data))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            len(self.cart.order_line),
            1,
            "The promotion shouldn't be applied as there is a reward choice",
        )
        res = response.json()
        claimable_rewards = res["claimable_rewards"]
        self.assertEqual(
            len(claimable_rewards), 2, "The two possible rewards should be claimable."
        )
        self.assertEqual(
            {claimable_rewards[0]["id"], claimable_rewards[1]["id"]},
            set(program.reward_ids.ids),
        )
        with self._create_test_client(router=cart_router) as test_client:
            data = {"reward_id": claimable_rewards[0]["id"]}
            response: Response = test_client.post(
                "/apply_reward", content=json.dumps(data)
            )
        self.assertEqual(response.status_code, 200)
