# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.sale_loyalty.tests.common import TestSaleCouponCommon

from ..routers.loyalty import loyalty_router


class TestShopinvaderSaleLoyaltyCommon(FastAPITransactionCase, TestSaleCouponCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "FastAPI Loyalty Demo"})
        cls.user_with_rights = cls.env["res.users"].create(
            {
                "name": "Test User With Rights",
                "login": "user_with_rights",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "shopinvader_api_sale_loyalty.shopinvader_loyalty_user_group"
                            ).id,
                        ],
                    )
                ],
            }
        )
        cls.default_fastapi_running_user = cls.user_with_rights
        cls.default_fastapi_authenticated_partner = partner.with_user(
            cls.user_with_rights
        )
        cls.default_fastapi_router = loyalty_router

    def setUp(self):
        super().setUp()
        self.gift_product_tag = self.env["product.tag"].create({"name": "Gift Product"})

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

    def _create_program_choice_reward_with_code(self, product):
        return self.env["loyalty.program"].create(
            {
                "name": "With coupon: Buy 1 product, choose 10% on all or 25% on cheapest",
                "program_type": "coupons",
                "trigger": "with_code",
                "applies_on": "current",
                "company_id": self.env.company.id,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "product_ids": [(4, product.id)],
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

    def _create_program_choice_reward_auto(self, product):
        return self.env["loyalty.program"].create(
            {
                "name": "Promotion: Buy 1 product, choose 10% on all or 25% on cheapest",
                "program_type": "promotion",
                "trigger": "auto",
                "applies_on": "current",
                "company_id": self.env.company.id,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "product_ids": [(4, product.id)],
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

    def _create_program_free_product_choice_with_code(self, rule_product, product_tag):
        return self.env["loyalty.program"].create(
            {
                "name": "With code: Choose 1B or 1C free if 1A bought",
                "program_type": "coupons",
                "trigger": "with_code",
                "applies_on": "current",
                "company_id": self.env.company.id,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "product_ids": [(4, rule_product.id)],
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

    def _create_program_free_product_choice_auto(self, rule_product, product_tag):
        return self.env["loyalty.program"].create(
            {
                "name": "Promotion: Choose 1B or 1C free if 1A bought",
                "program_type": "promotion",
                "trigger": "auto",
                "applies_on": "current",
                "company_id": self.env.company.id,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "product_ids": [(4, rule_product.id)],
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

    def _create_discount_code_program(self):
        return self.env["loyalty.program"].create(
            {
                "name": "50% on order with code 'PROMOTION'",
                "program_type": "promo_code",
                "trigger": "with_code",
                "applies_on": "current",
                "company_id": self.env.company.id,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "code": "PROMOTION",
                        },
                    )
                ],
                "reward_ids": [
                    (
                        0,
                        0,
                        {
                            "reward_type": "discount",
                            "discount": 50,
                            "required_points": 1,
                        },
                    ),
                ],
            }
        )
