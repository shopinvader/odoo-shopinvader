# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    # Public Methods

    def apply_coupon(self, **params):
        cart = self._get()
        self._apply_coupon(cart, params)
        return self._to_json(cart)

    def recompute_coupon_lines(self, **params):
        cart = self._get()
        self._recompute_coupon_lines(cart, params)
        return self._to_json(cart)

    # Private Methods

    def _check_code_and_reward(self, cart, code, reward_id=None):
        """
        * Check the code is valid.
        * Check the provided reward is allowed.
          If no reward is given, return the unique allowed reward,
          or raise an error.

          :return: the browsed reward
        """
        status = cart._try_apply_code(code)
        if "error" in status:
            raise UserError(status["error"])
        all_rewards = self.env["loyalty.reward"]
        for rewards in status.values():
            all_rewards |= rewards

        if not all_rewards:
            raise UserError(_("No reward available for this code."))
        if reward_id and reward_id not in all_rewards.ids:
            raise UserError(_("Reward not allowed for this code."))
        if not reward_id and len(all_rewards) > 1:
            raise UserError(_("Several rewards available. Please specify one."))

        if reward_id:
            return self.env["loyalty.reward"].browse(reward_id)
        return all_rewards[0]  # In this case only 1 reward available

    def _check_free_reward_product(self, reward, product_id=None):
        """
        Check the free product is allowed (if given) or check
        that it is unique (if not given).

        :return: the free product id
        """
        if not reward.reward_type == "product":
            return

        reward_products = reward.reward_product_ids

        if not reward_products:
            raise UserError(_("No free products available."))
        if product_id and product_id not in reward_products.ids:
            raise UserError(_("Free product not allowed for this reward."))
        if not product_id and len(reward_products) > 1:
            raise UserError(_("Several free products available. Please specify one."))

        if product_id:
            return product_id
        return reward_products[0].id

    def _apply_coupon(self, cart, params):
        """Apply a coupon or promotion code.

        It can raise UserError if coupon is not applicable, or
        if the coupon let the choice between several rewards, and the
        selected reward is not specified.
        """
        reward = self._check_code_and_reward(
            cart, params["code"], params.get("reward_id")
        )
        product_id = None
        if reward.reward_type == "product":
            product_id = self._check_free_reward_product(
                reward, params.get("free_product_id")
            )

        return (
            self.env["sale.loyalty.reward.wizard"]
            .create(
                {
                    "order_id": cart.id,
                    "selected_reward_id": reward.id if reward else None,
                    "selected_product_id": product_id if product_id else None,
                }
            )
            .action_apply()
        )

    def _recompute_coupon_lines(self, cart, params):
        """
        Call the reward wizard as when calling "Promotions" button.
        If no reward or a single reward must be applied, do it.
        If several rewards can be applied, do it if reward_id
        (and free_product_id if necessary) is specified.
        """
        res = cart.action_open_reward_wizard()
        if isinstance(res, bool):
            # This case happens when no available reward,
            # or a unique reward (in this case it was already applied)
            return

        if not params.get("reward_id"):
            raise UserError(_("Several rewards can be applied. Please specify one."))

        reward = self.env["loyalty.reward"].browse(params["reward_id"])
        product_id = self._check_free_reward_product(
            reward, params.get("free_product_id")
        )

        return self.env["sale.loyalty.reward.wizard"].create(
            {
                "order_id": cart.id,
                "selected_reward_id": params["reward_id"],
                "selected_product_id": product_id if product_id else None,
            }
        )

    # Private Overrides

    def _add_item(self, cart, params):
        skip_coupon_recompute = params.pop("skip_coupon_recompute", None)
        res = super()._add_item(cart, params)
        if not skip_coupon_recompute:
            self._recompute_coupon_lines(cart, params)
        return res

    def _update_item(self, cart, params, item=False):
        skip_coupon_recompute = params.pop("skip_coupon_recompute", None)
        res = super()._update_item(cart, params, item)
        if not skip_coupon_recompute:
            self._recompute_coupon_lines(cart, params)
        return res

    def _delete_item(self, cart, params):
        skip_coupon_recompute = params.pop("skip_coupon_recompute", None)
        res = super()._delete_item(cart, params)
        if not skip_coupon_recompute:
            self._recompute_coupon_lines(cart, params)
        return res

    def _get_lines_to_copy(self, cart):
        return super()._get_lines_to_copy(cart).filtered(lambda l: not l.is_reward_line)

    # Validator

    def _validator_apply_coupon(self):
        return {
            "code": {
                "type": "string",
                "required": True,
            },
            "reward_id": {
                "type": "integer",
                "coerce": to_int,
            },
            "free_product_id": {
                "coerce": to_int,
                "type": "integer",
            },
        }

    def _validator_recompute_coupon_lines(self):
        return {
            "reward_id": {
                "type": "integer",
                "coerce": to_int,
            },
            "free_product_id": {
                "type": "integer",
                "coerce": to_int,
            },
        }

    def _subvalidator_skip_coupon_recompute(self):
        return {
            "skip_coupon_recompute": {
                "type": "boolean",
                "required": False,
            }
        }

    def _validator_add_item(self):
        res = super()._validator_add_item()
        res.update(self._subvalidator_skip_coupon_recompute())
        return res

    def _validator_update_item(self):
        res = super()._validator_update_item()
        res.update(self._subvalidator_skip_coupon_recompute())
        return res

    def _validator_delete_item(self):
        res = super()._validator_delete_item()
        res.update(self._subvalidator_skip_coupon_recompute())
        return res
