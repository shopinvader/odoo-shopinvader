# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools.safe_eval import safe_eval

from odoo.addons.shopinvader_schema_sale.schemas import Sale as BaseSale

from ..schemas import (
    LoyaltyCard,
    LoyaltyProgram,
    LoyaltyRewardResponse as LoyaltyReward,
)


class Sale(BaseSale, extends=True):
    promo_codes: list[str] = []
    reward_amount: float = 0
    reward_amount_tax_incl: float = 0
    programs: list[LoyaltyProgram] = []
    generated_coupons: list[LoyaltyCard] = []
    claimable_rewards: list[LoyaltyReward] = []

    @classmethod
    def from_sale_order(cls, odoo_rec):
        obj = super().from_sale_order(odoo_rec)
        obj.promo_codes = safe_eval(odoo_rec.promo_codes)
        obj.reward_amount = odoo_rec.reward_amount
        obj.reward_amount_tax_incl = odoo_rec.reward_amount_tax_incl
        obj.programs = [
            LoyaltyProgram.from_loyalty_program(program)
            for program in odoo_rec.program_ids
        ]
        obj.generated_coupons = [
            LoyaltyCard.from_loyalty_card(card)
            for card in odoo_rec.generated_coupon_ids
        ]
        # Get claimable rewards
        odoo_rec._update_programs_and_rewards()
        claimable_rewards = odoo_rec._get_claimable_rewards()
        obj.claimable_rewards = []
        for _, rewards in claimable_rewards.items():
            obj.claimable_rewards += [
                LoyaltyReward.from_loyalty_reward(reward) for reward in rewards
            ]
        return obj
