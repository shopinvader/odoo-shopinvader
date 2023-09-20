# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# pylint: disable=method-required-super, consider-merging-classes-inherited


from odoo.addons.component.core import Component


class LoyaltyRewardService(Component):
    """Shopinvader service to get all rewards for a given coupon/rule code."""

    _inherit = "base.shopinvader.service"
    _name = "shopinvader.loyalty.reward.service"
    _usage = "reward"
    _expose_model = "loyalty.reward"
    _description = __doc__

    # Public Methods

    def get_rewards(self, **params):
        rewards = self._get_rewards(**params)
        return self._to_json(rewards)

    # Private methods

    def _get_rewards(self, **params):
        code = params["code"]
        card = self.env["loyalty.card"].search([("code", "=", code)], limit=1)
        program_id = self.env["loyalty.program"]
        if card:
            program_id = card.program_id
        else:
            rule_id = self.env["loyalty.rule"].search([("code", "=", code)], limit=1)
            if rule_id:
                program_id = rule_id.program_id
        if program_id:
            return program_id.reward_ids
        return self.env["loyalty.reward"]

    def _json_parser(self):
        res = [
            "id",
            "reward_type",
            "discount",
            "discount_mode",
            "discount_applicability",
            ("all_discount_product_ids:discount_products", ["id"]),
            ("reward_product_ids:reward_products", ["id"]),
        ]
        return res

    def _to_json(self, rewards, **kw):
        return rewards.jsonify(self._json_parser())

    # Validator

    def _validator_get_rewards(self):
        return {
            "code": {
                "type": "string",
                "required": True,
            },
        }
