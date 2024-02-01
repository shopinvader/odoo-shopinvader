# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel

from . import LoyaltyProgram


class LoyaltyRewardResponse(StrictExtendableBaseModel):
    id: int
    program: LoyaltyProgram
    reward_type: str
    discount: float | None = None
    discount_mode: str
    discount_applicability: str | None = None
    all_discount_product_ids: list[int] = []
    reward_product_ids: list[int] = []

    @classmethod
    def from_loyalty_reward(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            program=LoyaltyProgram.from_loyalty_program(odoo_rec.program_id),
            reward_type=odoo_rec.reward_type,
            discount=odoo_rec.discount or None,
            discount_mode=odoo_rec.discount_mode,
            discount_applicability=odoo_rec.discount_applicability or None,
            all_discount_product_ids=odoo_rec.all_discount_product_ids.ids,
            reward_product_ids=odoo_rec.reward_product_ids.ids,
        )


class LoyaltyRewardInput(StrictExtendableBaseModel):
    reward_id: int
    free_product_id: int | None = None
